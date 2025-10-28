from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response
from flask_login import login_required, current_user
from Models.base_model import db, get_local_time
from Models.users import Client
from Models.case import Case
from Models.payment import Payment
from sqlalchemy import or_
from .form import ClientForm

client_bp = Blueprint("client", __name__)

@client_bp.route('/add/client', methods=['GET', 'POST'])
@login_required
def add_client():
  """Add a new client"""
  form = ClientForm()
  
  if form.validate_on_submit():
    try:
      if form.email.data:
        existing_client = Client.query.filter_by(
          lawyer_id=current_user.id,
          email=form.email.data.lower().strip()
        ).first()
        
        if existing_client:
          flash('A client with this email already exists.', 'danger')
          return redirect(url_for('client.add_client'))
      
      # Create new client
      client = Client(
        lawyer_id=current_user.id,
        first_name=form.first_name.data.strip(),
        last_name=form.last_name.data.strip(),
        email=form.email.data.lower().strip() if form.email.data else None,
        phone=form.phone.data.strip() if form.phone.data else None,
        address=form.address.data.strip() if form.address.data else None,
        client_type=form.client_type.data,
        passwords = form.phone.data
      )
      
      db.session.add(client)
      db.session.commit()
      
      flash(f'Client {client.full_name} added successfully!', 'success')
      return redirect(url_for('dashboard.index'))
              
    except Exception as e:
      db.session.rollback()
      flash(f'Error: {str(e)} Please try again.', 'danger')
      return redirect(url_for('client.add_client'))
  
  context = {
     "form": form
  }

  return render_template('Main/add-client.html', **context)

@client_bp.route('/client/profile/<int:client_id>')
@login_required
def client_profile(client_id):
  """View client details and their cases"""
  try:
    client = Client.query.filter_by(
      unique_id=client_id,
      lawyer_id=current_user.id
    ).first()
    
    # Get client's cases
    cases = Case.query.filter_by(
      client_id=client.id
    ).order_by(Case.opened_date.desc()).all()
    
    context = {
      "client": client,
      "cases": cases,
    }

    return render_template(
      'Main/client-profile.html',
      **context
    )
      
  except Exception as e:
    flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('dashboard.index'))

@client_bp.route('/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
  """Edit client information"""
  try:
      client = Client.query.filter_by(
          id=client_id,
          user_id=current_user.id
      ).first()
      
      form = ClientForm(obj=client)
      
      if form.validate_on_submit():
          try:
              # Check if email is being changed and if it already exists
              if form.email.data and form.email.data.lower().strip() != client.email:
                  existing_client = Client.query.filter_by(
                      user_id=current_user.id,
                      email=form.email.data.lower().strip()
                  ).first()
                  
                  if existing_client and existing_client.id != client.id:
                      flash('A client with this email already exists.', 'error')
                      return render_template('clients/edit_client.html', form=form, client=client, title='Edit Client')
              
              # Update client information
              client.first_name = form.first_name.data.strip()
              client.last_name = form.last_name.data.strip()
              client.email = form.email.data.lower().strip() if form.email.data else None
              client.phone = form.phone.data.strip() if form.phone.data else None
              client.address = form.address.data.strip() if form.address.data else None
              client.client_type = form.client_type.data
              
              db.session.commit()
              
              flash(f'Client {client.full_name} updated successfully!', 'success')
              return redirect(url_for('clients.client_detail', client_id=client.id))
              
          except Exception as e:
              db.session.rollback()
              flash('An error occurred while updating the client. Please try again.', 'error')
      
      return render_template('clients/edit_client.html', form=form, client=client, title='Edit Client')
      
  except Exception as e:
      flash('Client not found or you do not have permission to edit this client.', 'error')
      return redirect(url_for('clients.index'))

@client_bp.route('/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    """Delete a client"""
    try:
        client = Client.query.filter_by(
            id=client_id,
            user_id=current_user.id
        ).first()
        
        client_name = client.full_name
        
        # Check if client has cases
        case_count = Case.query.filter_by(client_id=client_id).count()
        if case_count > 0:
            flash(f'Cannot delete client {client_name} because they have {case_count} active case(s).', 'error')
            return redirect(url_for('clients.client_detail', client_id=client_id))
        
        db.session.delete(client)
        db.session.commit()
        
        flash(f'Client {client_name} deleted successfully.', 'success')
        return redirect(url_for('clients.index'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the client. Please try again.', 'error')
        return redirect(url_for('clients.index'))

# API endpoint for client search (for autocomplete)
@client_bp.route('/api/search')
@login_required
def api_search():
    """API endpoint for client search (used for autocomplete)"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return jsonify([])
        
        clients = Client.query.filter_by(user_id=current_user.id).filter(
            or_(
                Client.first_name.ilike(f'%{query}%'),
                Client.last_name.ilike(f'%{query}%'),
                Client.email.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        results = [{
            'id': client.id,
            'name': client.full_name,
            'email': client.email,
            'phone': client.phone
        } for client in clients]
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify([])
