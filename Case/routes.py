from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response
from flask_login import login_required, current_user
from Models.base_model import db, get_local_time
from Models.users import Client, Lawyers
from Models.case import Case, CaseNote, CaseFiles
from Models.event import Event
from Models.payment import Payment
from .form import CaseForm, CaseNoteForm, PaymentForm, EventForm
from sqlalchemy import or_, desc
from datetime import date
from slugify import slugify
from decorator import role_required
from .aws_credentials import awsCredentials
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import boto3

case_bp = Blueprint("case", __name__)
s3 = boto3.resource(
  "s3",
  aws_access_key_id = awsCredentials.aws_access_key,
  aws_secret_access_key = awsCredentials.aws_secret_key
)
bucket_name = awsCredentials.bucket_name
region = awsCredentials.region

@case_bp.route('/new-case/<int:client_id>', methods=['GET', 'POST'])
@login_required
@role_required(["Lawyer"])
def add_case(client_id):
  """Add a new case"""
  form = CaseForm()
  
  client = Client.query.filter_by(unique_id=client_id, lawyer_id=current_user.id).first()
  if not client:
    flash('Invalid client selected.', 'danger')
    return redirect(url_for('dashboard.index'))

  if form.validate_on_submit():
    try:         
      # Create new case
      case = Case(
        title=form.title.data.strip(),
        alias=slugify(form.title.data.strip()),
        description=form.description.data.strip() if form.description.data else None,
        case_type=form.case_type.data,
        court_name=form.court_name.data.strip() if form.court_name.data else None,
        case_number=form.case_number.data.strip() if form.case_number.data else None,
        opposing_party=form.opposing_party.data.strip() if form.opposing_party.data else None,
        opposing_counsel=form.opposing_counsel.data.strip() if form.opposing_counsel.data else None,
        client_id=client.id,
        lawyer_id=current_user.id
      )
      
      db.session.add(case)
      db.session.commit()
      
      # Add initial case note
      if form.description.data:
        initial_note = CaseNote(
          case_id=case.id,
          content="Case opened",
          is_internal=False,
          is_editable=False,
        )
        db.session.add(initial_note)
        db.session.commit()
      
      flash(f'Case "{case.title}" created successfully!', 'success')
      return redirect(url_for('case.case_detail', case_id=case.alias))
        
    except Exception as e:
      db.session.rollback()
      flash(f'Error: {str(e)}', 'danger')
      return redirect(url_for('case.add_case', client_id=client.unique_id))
  
  context = {
    "form": form,
    "client": client,
    "back_url": request.referrer,
  }

  return render_template('Main/new-case.html', **context)

@case_bp.route('/case-details/<string:case_id>')
@login_required
def case_detail(case_id):
  """View case details with notes, payments, and events"""
  try:
    case = Case.query.filter_by(alias=case_id, lawyer_id=current_user.id).first()
    
    # Get case notes (both internal and client visible)
    client = Client.query.get(case.client_id)

    notes = CaseNote.query.filter_by(case_id=case.id).order_by(desc(CaseNote.created_at)).all()
    
    # Get payments
    payments = Payment.query.filter_by(case_id=case.id).order_by(desc(Payment.date_received)).all()
    
    # Get upcoming events
    upcoming_events = Event.query.filter_by(case_id=case.id).filter(
      Event.event_date >= date.today()
    ).order_by(Event.event_date, Event.event_time).limit(5).all()
    
    # Calculate total payments
    total_payments = sum(payment.amount for payment in payments)
    
    # Forms for adding new items
    note_form = CaseNoteForm()
    payment_form = PaymentForm()
    event_form = EventForm()

    context = {
      "case": case,
      "notes": notes,
      "case_files": CaseFiles.query.all(),
      "client": client,
      "payments": payments,
      "upcoming_events": upcoming_events,
      "total_payments": total_payments,
      "note_form": note_form,
      "payment_form": payment_form,
      "event_form": event_form,
    }
    
    return render_template('Main/case-details.html', **context)
      
  except Exception as e:
    flash(f'Error: {str(e)}', 'danger')
    return redirect(request.referrer)

@case_bp.route('/client/case-details/<string:case_id>')
@login_required
def client_case_detail(case_id):
  """View case details with notes, payments, and events"""
  try:
    case = Case.query.filter_by(alias=case_id, client_id=current_user.id).first()
    
    lawyer = Lawyers.query.get(case.lawyer_id)

    notes = CaseNote.query.filter_by(case_id=case.id, is_internal=False).order_by(desc(CaseNote.created_at)).all()
    
    # Get payments
    payments = Payment.query.filter_by(case_id=case.id).order_by(desc(Payment.date_received)).all()
    
    # Get upcoming events
    upcoming_events = Event.query.filter_by(case_id=case.id).filter(
      Event.event_date >= date.today()
    ).order_by(Event.event_date, Event.event_time).limit(5).all()
    
    # Calculate total payments
    total_payments = sum(payment.amount for payment in payments)

    context = {
      "case": case,
      "notes": notes,
      "case_files": CaseFiles.query.all(),
      "lawyer": lawyer,
      "payments": payments,
      "upcoming_events": upcoming_events,
      "total_payments": total_payments,
    }
    
    return render_template('Client/case-detail.html', **context)
      
  except Exception as e:
    flash(f'Error: {str(e)}', 'danger')
    return redirect(request.referrer)

@case_bp.route('/new-note/<int:case_id>', methods=['POST'])
@login_required
def add_note(case_id):
  """Add a note to a case"""
  form = CaseNoteForm()
  if form.validate_on_submit():
    try:
      case = Case.query.filter_by(unique_id=case_id, lawyer_id=current_user.id).first()

      if not case:
        flash("Case not found", "danger")
        return redirect(request.referrer)
    
      note = CaseNote(
        case_id=case.id,
        content=form.content.data.strip(),
        is_internal=False if form.is_internal.data == "False" else True
      )
      db.session.add(note)
      db.session.commit()

      if form.case_files.data:
        files = request.files.getlist("case_files")
        upload_file(note.id, files, case.id)

      flash('Note added successfully!', 'success')
      return redirect(url_for('case.case_detail', case_id=case.alias))
          
    except Exception as e:
      db.session.rollback()
      flash(f'Error:{str(e)}', 'danger')
      return redirect(url_for('case.case_detail', case_id=case.alias))

  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"{err_msg}", "danger")
    return redirect(url_for('admin.dashboard'))

def upload_file(note_id, files, case_id):
  case_note = CaseNote.query.get(note_id)
  case = Case.query.get(case_id)
  try:
    for file in files:
      filename = f"{case.alias}/{file.filename}"
      filetype = file.filename.split(".")[-1]
      case_files = CaseFiles(
        file_name = filename,
        case_note_id = case_note.id,
        file_type = filetype
      )
      s3.Bucket(bucket_name).upload_fileobj(file, filename)
      db.session.add(case_files)
      db.session.commit()
    flash("Files uploaded successfully", "success")
  except NoCredentialsError:
    db.session.rollback()
    flash("Credentials not available", "danger")
    return redirect(url_for('case.case_detail', case_id=case.alias))
  except PartialCredentialsError:
    db.session.rollback()
    flash("Incomplete credentials provided", "danger")
    return redirect(url_for('case.case_detail', case_id=case.alias))
  except ClientError as e:
    db.session.rollback()
    flash(f"Client Error: {e.response['Error']['Message']}", "danger")
    return redirect(url_for('case.case_detail', case_id=case.alias))
  except Exception as e:
    db.session.rollback()
    flash(f"Error: {repr(e)}", "danger")
    return redirect(url_for('case.case_detail', case_id=case.alias))

@login_required
def remove_case_files(case_file):
  s3.Bucket(bucket_name).Object(case_file.file_name).delete()
  db.session.commit()

@case_bp.route('/<string:case_id>/<int:case_note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_case_note(case_id, case_note_id):
  """Edit case information"""
  try:
    case = Case.query.filter_by(alias=case_id, lawyer_id=current_user.id).first()

    if not case:
      flash("Case not found", "danger")
      return redirect(request.referrer)

    case_note = CaseNote.query.filter_by(unique_id=case_note_id, case_id=case.id).first()

    if not case_note:
      flash("Case note not found", "danger")
      return redirect(url_for('case.case_detail', case_id=case.alias))
    
    form = CaseNoteForm(obj=case_note)
    
    if form.validate_on_submit():
      case_note.content = form.content.data
      if form.is_internal.data == "False":
         case_note.is_internal = False
      elif form.is_internal.data == "True":
         case_note.is_internal = True
      db.session.commit()
      
      flash('Case note updated successfully!', 'success')
      return redirect(url_for('case.case_detail', case_id=case.alias))
    
    context = {
      "form": form,
      "case": case,
      "case_note": case_note,
      "back_url": url_for('case.case_detail', case_id=case.alias)
    }

    return render_template('Main/edit-case-note.html', **context)
      
  except Exception as e:
    db.session.rollback()
    flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('case.case_detail', case_id=case.alias))

@case_bp.route('/remove-note/<int:note_id>/<string:case_id>')
@login_required
def remove_case_note(note_id, case_id):
  """Add a note to a case"""
  case = Case.query.filter_by(alias=case_id).first()

  if not case:
    flash("Case not found", "danger")
    return redirect(request.referrer)

  case_note = CaseNote.query.filter_by(unique_id=note_id, case_id=case.id).first()

  if not case_note:
    flash("Case note not found", "danger")
    return redirect(url_for('case.case_detail', case_id=case.alias))
  
  case_files = CaseFiles.query.filter_by(case_note_id=case_note.id).all()
  for case_file in case_files:
    remove_case_files(case_file)
      
  try:
    db.session.delete(case_note)
    db.session.commit()
    
    flash('Note removed successfully!', 'success')
    return redirect(url_for('case.case_detail', case_id=case.alias))
        
  except Exception as e:
    db.session.rollback()
    flash(f'Error:{str(e)}', 'danger')
    return redirect(url_for('case.case_detail', case_id=case.alias))

@case_bp.route('/<int:case_id>/add-payment', methods=['POST'])
@login_required
def add_payment(case_id):
  """Add a payment to a case"""
  form = PaymentForm()
  
  if form.validate_on_submit():
    try:
      case = Case.query.filter_by(unique_id=case_id, lawyer_id=current_user.id).first()

      if not case:
        flash("Case not found", "danger")
        return redirect(request.referrer)
    
      payment = Payment(
        case_id=case.id,
        amount=form.amount.data,
        payment_method=form.payment_method.data,
        reference=form.reference.data.strip() if form.reference.data else None,
      )
      
      db.session.add(payment)
      db.session.commit()
      
      # Add automatic note about payment
      payment_note = CaseNote(
        case_id=case.id,
        content=f"Payment of Ksh{form.amount.data} received via {form.payment_method.data}",
        is_internal=False,
        is_editable=False,
      )
      db.session.add(payment_note)
      db.session.commit()
      
      flash('Payment recorded successfully!', 'success')

    except Exception as e:
      db.session.rollback()
      flash(f'Error: {str(e)}', 'danger')

  else:
    for field, errors in form.errors.items():
      for error in errors:
        flash(f'{getattr(form, field).label.text}: {error}', 'danger')
  
  return redirect(url_for('case.case_detail', case_id=case.alias))

@case_bp.route('/<int:case_id>/add_event', methods=['POST'])
@login_required
def add_event(case_id):
    """Add an event to a case"""
    try:
        case = Case.query.filter_by(
            id=case_id,
            user_id=current_user.id
        ).first_or_404()
        
        form = EventForm()
        
        if form.validate_on_submit():
            event = Event(
                case_id=case_id,
                title=form.title.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                event_date=form.event_date.data,
                event_time=form.event_time.data if form.event_time.data else None,
                event_type=form.event_type.data
            )
            
            db.session.add(event)
            db.session.commit()
            
            # Add automatic note about event
            event_note = CaseNote(
                case_id=case_id,
                content=f"Event scheduled: {form.title.data} on {form.event_date.data}",
                is_internal=False
            )
            db.session.add(event_note)
            db.session.commit()
            
            flash('Event added successfully!', 'success')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while adding the event.', 'error')
    
    return redirect(url_for('cases.case_detail', case_id=case_id))

@case_bp.route('/<int:case_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_case(case_id):
  """Edit case information"""
  try:
    case = Case.query.filter_by(unique_id=case_id, lawyer_id=current_user.id).first()

    if not case:
      flash("Case not found", "danger")
      return redirect(request.referrer)
    
    form = CaseForm(obj=case)
    
    if form.validate_on_submit():
      form.populate_obj(case)
      db.session.commit()
      
      flash('Case updated successfully!', 'success')
      return redirect(url_for('case.case_detail', case_id=case.alias))
    
    context = {
      "form": form,
      "case": case,
      "back_url": url_for('case.case_detail', case_id=case.alias)
    }

    return render_template('Main/edit-case.html', **context)
      
  except Exception as e:
    db.session.rollback()
    flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('case.case_detail', case_id=case.alias))

@case_bp.route('/<int:case_id>/close', methods=['POST'])
@login_required
def close_case(case_id):
  """Delete a case"""
  try:
    case = Case.query.filter_by(
      unique_id=case_id,
      lawyer_id=current_user.id
    ).first()
    
    case.status = "Closed"
    db.session.commit()
    
    flash(f'Case closed successfully.', 'success')
    return redirect(url_for('dashboard.index'))
      
  except Exception as e:
    db.session.rollback()
    flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('case.case_detail', case_id=case_id))

# API endpoints for calendar and dashboard
@case_bp.route('/api/upcoming_events')
@login_required
def api_upcoming_events():
    """API endpoint for upcoming events (used in dashboard)"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        events = Event.query.join(Case).filter(
            Case.user_id == current_user.id,
            Event.event_date >= date.today()
        ).order_by(Event.event_date, Event.event_time).limit(limit).all()
        
        results = [{
            'id': event.id,
            'title': event.title,
            'date': event.event_date.isoformat(),
            'time': event.event_time,
            'type': event.event_type,
            'case_title': event.case.title,
            'case_id': event.case_id
        } for event in events]
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify([])

@case_bp.route('/api/case_stats')
@login_required
def api_case_stats():
    """API endpoint for case statistics"""
    try:
        stats = {
            'total': Case.query.filter_by(user_id=current_user.id).count(),
            'active': Case.query.filter_by(user_id=current_user.id, status='active').count(),
            'pending': Case.query.filter_by(user_id=current_user.id, status='pending').count(),
            'closed': Case.query.filter_by(user_id=current_user.id, status='closed').count()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({})
