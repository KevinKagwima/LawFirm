from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response
from flask_login import login_required, current_user
from Models.base_model import db, get_local_time
from Models.users import Lawyers, Client
from Models.case import Case, CaseNote
from Models.event import Event
from Models.payment import Payment
from .form import CaseForm, CaseNoteForm, PaymentForm, EventForm
from sqlalchemy import or_, desc
from datetime import date, datetime

case_bp = Blueprint("case", __name__)

@case_bp.route('/')
@login_required
def index():
    """Display all cases for the current lawyer"""
    try:
        # Get parameters
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        case_type_filter = request.args.get('type', '')
        search_query = request.args.get('search', '').strip()
        per_page = 12
        
        # Build query
        query = Case.query.filter_by(user_id=current_user.id)
        
        # Apply filters
        if status_filter:
            query = query.filter(Case.status == status_filter)
        if case_type_filter:
            query = query.filter(Case.case_type == case_type_filter)
        if search_query:
            search_filter = or_(
                Case.title.ilike(f'%{search_query}%'),
                Case.description.ilike(f'%{search_query}%'),
                Case.case_number.ilike(f'%{search_query}%'),
                Case.opposing_party.ilike(f'%{search_query}%'),
                Client.first_name.ilike(f'%{search_query}%'),
                Client.last_name.ilike(f'%{search_query}%')
            )
            query = query.join(Client).filter(search_filter)
        
        # Order by most recently updated
        cases = query.order_by(desc(Case.opened_date)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get stats for filters
        case_stats = {
            'total': Case.query.filter_by(user_id=current_user.id).count(),
            'active': Case.query.filter_by(user_id=current_user.id, status='active').count(),
            'pending': Case.query.filter_by(user_id=current_user.id, status='pending').count(),
            'closed': Case.query.filter_by(user_id=current_user.id, status='closed').count()
        }
        
        return render_template(
            'cases/index.html',
            cases=cases,
            search_query=search_query,
            status_filter=status_filter,
            case_type_filter=case_type_filter,
            case_stats=case_stats,
            title='Cases'
        )
        
    except Exception as e:
        flash('An error occurred while loading cases.', 'error')
        return redirect(url_for('dashboard.index'))

@case_bp.route('/new-case/<int:client_id>', methods=['GET', 'POST'])
@login_required
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
          is_internal=False
        )
        db.session.add(initial_note)
        db.session.commit()
      
      flash(f'Case "{case.title}" created successfully!', 'success')
      return redirect(url_for('case.case_detail', case_id=case.unique_id))
        
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

@case_bp.route('/case-details/<int:case_id>')
@login_required
def case_detail(case_id):
  """View case details with notes, payments, and events"""
  try:
    case = Case.query.filter_by(unique_id=case_id, lawyer_id=current_user.id).first()
    
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
    return redirect(url_for('dashboard.index'))

@case_bp.route('/new-note/<int:case_id>', methods=['POST', 'GET'])
@login_required
def add_note(case_id):
  """Add a note to a case"""
  case = Case.query.filter_by(unique_id=case_id, lawyer_id=current_user.id).first()

  if not case:
    flash("Case not found", "danger")
    return redirect(request.referrer)
  
  form = CaseNoteForm()
    
  if form.validate_on_submit():
    try:
      note = CaseNote(
        case_id=case.id,
        content=form.content.data.strip(),
        is_internal=bool(form.is_internal.data)
      )
      
      db.session.add(note)
      db.session.commit()
      
      flash('Note added successfully!', 'success')
      return redirect(url_for('case.case_detail', case_id=case.unique_id))
          
    except Exception as e:
      db.session.rollback()
      flash(f'Error:{str(e)}', 'danger')
      return redirect(url_for('case.case_detail', case_id=case.unique_id))

  context = {
    "form": form,
    "case": case,
    "back_url": request.referrer,
  }

  return render_template("Main/add-case-note.html", **context)

@case_bp.route('/remove-note/<int:note_id>/<int:case_id>')
@login_required
def remove_case_note(note_id, case_id):
  """Add a note to a case"""
  case = Case.query.filter_by(unique_id=case_id).first()

  if not case:
    flash("Case not found", "danger")
    return redirect(request.referrer)

  case_note = CaseNote.query.filter_by(unique_id=note_id, case_id=case.id).first()

  if not case_note:
    flash("Case note not found", "danger")
    return redirect(url_for('case.case_detail', case_id=case.unique_id))
      
  try:
    db.session.delete(case_note)
    db.session.commit()
    
    flash('Note removed successfully!', 'success')
    return redirect(url_for('case.case_detail', case_id=case.unique_id))
        
  except Exception as e:
    db.session.rollback()
    flash(f'Error:{str(e)}', 'danger')
    return redirect(url_for('case.case_detail', case_id=case.unique_id))

@case_bp.route('/<int:case_id>/add_payment', methods=['POST'])
@login_required
def add_payment(case_id):
    """Add a payment to a case"""
    try:
        case = Case.query.filter_by(
            id=case_id,
            user_id=current_user.id
        ).first_or_404()
        
        form = PaymentForm()
        
        if form.validate_on_submit():
            payment = Payment(
                case_id=case_id,
                amount=form.amount.data,
                date_received=form.date_received.data,
                payment_method=form.payment_method.data,
                reference=form.reference.data.strip() if form.reference.data else None,
                notes=form.notes.data.strip() if form.notes.data else None
            )
            
            db.session.add(payment)
            db.session.commit()
            
            # Add automatic note about payment
            payment_note = CaseNote(
                case_id=case_id,
                content=f"Payment received: ${form.amount.data:.2f} via {form.payment_method.data}",
                is_internal=False
            )
            db.session.add(payment_note)
            db.session.commit()
            
            flash('Payment recorded successfully!', 'success')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{getattr(form, field).label.text}: {error}', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while recording the payment.', 'error')
    
    return redirect(url_for('cases.case_detail', case_id=case_id))

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
        case = Case.query.filter_by(
            id=case_id,
            user_id=current_user.id
        ).first_or_404()
        
        form = CaseForm(obj=case)
        
        if form.validate_on_submit():
            case.title = form.title.data.strip()
            case.description = form.description.data.strip() if form.description.data else None
            case.case_type = form.case_type.data
            case.status = form.status.data
            case.court_name = form.court_name.data.strip() if form.court_name.data else None
            case.case_number = form.case_number.data.strip() if form.case_number.data else None
            case.opposing_party = form.opposing_party.data.strip() if form.opposing_party.data else None
            case.opposing_counsel = form.opposing_counsel.data.strip() if form.opposing_counsel.data else None
            
            # If closing case, set closed date
            if form.status.data == 'closed' and not case.closed_date:
                case.closed_date = datetime.utcnow()
            elif form.status.data != 'closed':
                case.closed_date = None
            
            db.session.commit()
            
            flash(f'Case "{case.title}" updated successfully!', 'success')
            return redirect(url_for('cases.case_detail', case_id=case.id))
        
        return render_template('cases/edit_case.html', form=form, case=case, title='Edit Case')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the case.', 'error')
        return redirect(url_for('cases.case_detail', case_id=case_id))

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
