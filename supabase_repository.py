# Supabase Repository - PostgreSQL version of PolicyRepository
import hashlib
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple, Dict, Any
from supabase_config import get_supabase_client
from supabase import Client

class SupabaseRepository:
    def __init__(self):
        self.supabase: Client = get_supabase_client()
        self._ensure_default_data()

    def _ensure_default_data(self):
        """Ensure default data exists in the database"""
        try:
            # Check if admin user exists
            result = self.supabase.table('users').select('*').eq('username', 'admin').execute()
            if not result.data:
                # Create default admin user
                self.create_user('admin', 'admin123', True, None)
                print("Default admin user created")
        except Exception as e:
            print(f"Error ensuring default data: {e}")

    # User Management
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user with username and password"""
        try:
            result = self.supabase.table('users').select('password_hash').eq('username', username).execute()
            if result.data:
                stored_hash = result.data[0]['password_hash']
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if stored_hash == password_hash:
                    # Update last login
                    self.supabase.table('users').update({
                        'last_login': datetime.now().isoformat()
                    }).eq('username', username).execute()
                    return True
            return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def create_user(self, username: str, password: str, is_admin: bool = False, company_id: Optional[int] = None) -> bool:
        """Create a new user"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            result = self.supabase.table('users').insert({
                'username': username,
                'password_hash': password_hash,
                'is_admin': is_admin,
                'company_id': company_id,
                'created_at': datetime.now().isoformat()
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    def is_user_admin(self, username: str) -> bool:
        """Check if user is admin"""
        try:
            result = self.supabase.table('users').select('is_admin').eq('username', username).execute()
            return result.data[0]['is_admin'] if result.data else False
        except Exception:
            return False

    def get_user_company_id(self, username: str) -> Optional[int]:
        """Get user's company ID"""
        try:
            result = self.supabase.table('users').select('company_id').eq('username', username).execute()
            return result.data[0]['company_id'] if result.data else None
        except Exception:
            return None

    def get_all_users(self, current_user: str = None) -> List[Tuple]:
        """Get all users filtered by current user's permissions"""
        try:
            if current_user and self.is_user_admin(current_user):
                # Admin sees all users
                result = self.supabase.table('users').select('id, username, is_admin, created_at, last_login, company_id').order('username').execute()
            elif current_user:
                # Regular users see only their company users
                user_company_id = self.get_user_company_id(current_user)
                if user_company_id:
                    result = self.supabase.table('users').select('id, username, is_admin, created_at, last_login, company_id').eq('company_id', user_company_id).order('username').execute()
                else:
                    return []
            else:
                return []
            
            # Convert to tuple format for compatibility
            users = []
            for user in result.data:
                users.append((
                    user['id'],
                    user['username'],
                    user['is_admin'],
                    user['created_at'],
                    user['last_login'],
                    user['company_id']
                ))
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        try:
            result = self.supabase.table('users').delete().eq('username', username).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def get_user_by_id(self, user_id: int) -> Optional[Tuple]:
        """Get user by ID"""
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            if result.data:
                user = result.data[0]
                return (user['id'], user['username'], user['is_admin'], user['created_at'], user['last_login'], user['company_id'])
            return None
        except Exception:
            return None

    # Company Management
    def get_all_companies(self) -> List[Tuple]:
        """Get all companies"""
        try:
            result = self.supabase.table('companies').select('*').order('name').execute()
            companies = []
            for company in result.data:
                companies.append((
                    company['id'],
                    company['name'],
                    company['created_at'],
                    company['active']
                ))
            return companies
        except Exception as e:
            print(f"Error getting companies: {e}")
            return []

    def add_company(self, name: str) -> bool:
        """Add a new company"""
        try:
            result = self.supabase.table('companies').insert({
                'name': name,
                'created_at': datetime.now().isoformat(),
                'active': True
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error adding company: {e}")
            return False

    def get_company_by_id(self, company_id: int) -> Optional[Tuple]:
        """Get company by ID"""
        try:
            result = self.supabase.table('companies').select('*').eq('id', company_id).execute()
            if result.data:
                company = result.data[0]
                return (company['id'], company['name'], company['created_at'], company['active'])
            return None
        except Exception:
            return None

    def update_company_status(self, company_id: int, active: bool) -> bool:
        """Update company active status"""
        try:
            result = self.supabase.table('companies').update({'active': active}).eq('id', company_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating company status: {e}")
            return False

    def delete_company(self, company_id: int) -> bool:
        """Delete a company"""
        try:
            result = self.supabase.table('companies').delete().eq('id', company_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error deleting company: {e}")
            return False

    # Permission Management
    def check_permission(self, username: str, permission_name: str) -> bool:
        """Check if user has specific permission"""
        try:
            # Get user ID first
            user_result = self.supabase.table('users').select('id').eq('username', username).execute()
            if not user_result.data:
                return False
            
            user_id = user_result.data[0]['id']
            
            # Check permission
            result = self.supabase.table('user_permissions').select('permission_value').eq('user_id', user_id).eq('permission_name', permission_name).execute()
            return result.data[0]['permission_value'] if result.data else False
        except Exception:
            return False

    def get_user_permissions(self, username: str) -> Dict[str, bool]:
        """Get all permissions for a user"""
        try:
            # Get user ID first
            user_result = self.supabase.table('users').select('id').eq('username', username).execute()
            if not user_result.data:
                return {}
            
            user_id = user_result.data[0]['id']
            
            # Get all permissions
            result = self.supabase.table('user_permissions').select('permission_name, permission_value').eq('user_id', user_id).execute()
            
            permissions = {}
            for perm in result.data:
                permissions[perm['permission_name']] = perm['permission_value']
            return permissions
        except Exception as e:
            print(f"Error getting user permissions: {e}")
            return {}

    def set_user_permissions(self, username: str, permissions: Dict[str, bool]) -> bool:
        """Set user permissions"""
        try:
            # Get user ID first
            user_result = self.supabase.table('users').select('id').eq('username', username).execute()
            if not user_result.data:
                return False
            
            user_id = user_result.data[0]['id']
            
            # Update each permission
            for perm_name, perm_value in permissions.items():
                # Try to update existing permission
                existing = self.supabase.table('user_permissions').select('id').eq('user_id', user_id).eq('permission_name', perm_name).execute()
                
                if existing.data:
                    # Update existing
                    self.supabase.table('user_permissions').update({
                        'permission_value': perm_value,
                        'updated_at': datetime.now().isoformat()
                    }).eq('user_id', user_id).eq('permission_name', perm_name).execute()
                else:
                    # Insert new
                    self.supabase.table('user_permissions').insert({
                        'user_id': user_id,
                        'permission_name': perm_name,
                        'permission_value': perm_value,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }).execute()
            
            return True
        except Exception as e:
            print(f"Error setting user permissions: {e}")
            return False

    def set_user_permission(self, username: str, permission_name: str, permission_value: bool) -> bool:
        """Set single user permission"""
        try:
            # Get user ID
            user_result = self.supabase.table('users').select('id').eq('username', username).execute()
            if not user_result.data:
                return False
            
            user_id = user_result.data[0]['id']
            now = datetime.now().isoformat()
            
            # Check if permission already exists
            existing_result = self.supabase.table('user_permissions').select('id').eq('user_id', user_id).eq('permission_name', permission_name).execute()
            
            if existing_result.data:
                # Update existing permission
                self.supabase.table('user_permissions').update({
                    'permission_value': permission_value,
                    'updated_at': now
                }).eq('user_id', user_id).eq('permission_name', permission_name).execute()
            else:
                # Insert new permission
                self.supabase.table('user_permissions').insert({
                    'user_id': user_id,
                    'permission_name': permission_name,
                    'permission_value': permission_value,
                    'created_at': now,
                    'updated_at': now
                }).execute()
            
            return True
        except Exception as e:
            print(f"Error setting user permission: {e}")
            return False

    def copy_user_permissions(self, template_username: str, target_username: str) -> bool:
        """Copy permissions from template user to target user"""
        try:
            # Get template user's permissions
            template_user_result = self.supabase.table('users').select('id').eq('username', template_username).execute()
            if not template_user_result.data:
                print(f"Template user not found: {template_username}")
                return False
            
            template_user_id = template_user_result.data[0]['id']
            
            # Get target user ID
            target_user_result = self.supabase.table('users').select('id').eq('username', target_username).execute()
            if not target_user_result.data:
                print(f"Target user not found: {target_username}")
                return False
            
            target_user_id = target_user_result.data[0]['id']
            
            # Get template user's permissions
            template_permissions = self.supabase.table('user_permissions').select('*').eq('user_id', template_user_id).execute()
            
            if not template_permissions.data:
                print(f"No permissions found for template user: {template_username}")
                return True  # Not an error, just no permissions to copy
            
            # Copy each permission to target user
            for perm in template_permissions.data:
                success = self.set_user_permission(
                    target_username, 
                    perm['permission_name'], 
                    perm['permission_value']
                )
                if not success:
                    print(f"Failed to copy permission {perm['permission_name']} to {target_username}")
                    return False
            
            print(f"Successfully copied {len(template_permissions.data)} permissions from {template_username} to {target_username}")
            return True
        except Exception as e:
            print(f"Error copying user permissions: {e}")
            return False

    def apply_role_template(self, username: str, role_name: str) -> bool:
        """Apply role template to user"""
        role_templates = {
            "YÖNETİCİ": {
                "policies_view": True,
                "policies_add": True,
                "policies_edit": True,
                "policies_delete": True,
                "renewals_view": True,
                "renewals_edit": True,
                "renewals_status_update": True,
                "documents_upload": True,
                "documents_view": True,
                "documents_delete": True,
                "accounts_view": True,
                "accounts_add": True,
                "accounts_edit": True,
                "accounts_delete": True,
                "cross_selling_view": True,
                "cross_selling_add": True,
                "cross_selling_edit": True,
                "cross_selling_delete": True,
                "reports_view": True,
                "reports_generate": True,
                "settings_view": True,
                "settings_edit": True,
                "products_manage": True,
                "users_view": True,
                "users_add": True,
                "users_edit": True,
                "users_delete": True,
                "permissions_manage": True
            },
            "SATIŞÇI": {
                "policies_add": True,
                "policies_edit": True,
                "renewals_view": True,
                "documents_view": True,
                "reports_view": True
            },
            "MUHASEBECİ": {
                "policies_view": True,
                "documents_view": True,
                "reports_view": True
            },
            "OPERATÖR": {
                "policies_view": True,
                "policies_add": True,
                "policies_edit": True,
                "policies_delete": True,
                "renewals_view": True,
                "renewals_edit": True,
                "renewals_status_update": True,
                "documents_upload": True,
                "documents_view": True,
                "documents_delete": True
            }
        }
        
        if role_name in role_templates:
            return self.set_user_permissions(username, role_templates[role_name])
        return False

    # Products Management
    def get_all_products(self) -> List[Tuple]:
        """Get all products"""
        try:
            result = self.supabase.table('products').select('*').order('name').execute()
            products = []
            for product in result.data:
                products.append((
                    product['id'],
                    product['name'],
                    product['commission_percent']
                ))
            return products
        except Exception as e:
            print(f"Error getting products: {e}")
            return []

    def get_products(self) -> List[Tuple]:
        """Get all products (alias for compatibility)"""
        return self.get_all_products()

    # Policies Management (basic structure - can be expanded)
    def get_all_policies(self, current_user: str = None) -> List[Tuple]:
        """Get all policies filtered by user's company"""
        try:
            if current_user and self.is_user_admin(current_user):
                # Admin sees all policies
                result = self.supabase.table('policies').select('*').order('id', desc=True).execute()
            elif current_user:
                # Regular users see only their company policies
                user_company_id = self.get_user_company_id(current_user)
                if user_company_id:
                    result = self.supabase.table('policies').select('*').eq('company_id', user_company_id).order('id', desc=True).execute()
                else:
                    return []
            else:
                return []
            
            # Convert to tuple format for compatibility
            policies = []
            for policy in result.data:
                policies.append((
                    policy['id'],
                    policy['end_date'],
                    policy['customer_name'],
                    policy['customer_tc_vkn'],
                    policy['plate'],
                    policy['doc_serial'],
                    policy['note'],
                    policy['premium'],
                    policy['product_id'],
                    policy['salesperson_id'],
                    policy['policy_number'],
                    policy['company_id'],
                    policy['last_notified_on']
                ))
            return policies
        except Exception as e:
            print(f"Error getting policies: {e}")
            return []

    def get_all_policies_enriched(self, current_user: str | None = None) -> List[Tuple]:
        """Return policies in UI-expected 17-field tuple format with names."""
        try:
            # Fetch policies per permissions
            if current_user and self.is_user_admin(current_user):
                result = self.supabase.table('policies').select('*').order('id', desc=True).execute()
            elif current_user:
                user_company_id = self.get_user_company_id(current_user)
                if user_company_id:
                    result = self.supabase.table('policies').select('*').eq('company_id', user_company_id).order('id', desc=True).execute()
                else:
                    return []
            else:
                return []

            enriched: List[Tuple] = []
            for policy in result.data:
                # Defaults
                product_name = ""
                company_name = ""
                salesperson_name = ""
                commission_percent = 0

                try:
                    if policy.get('product_id'):
                        pr = self.supabase.table('products').select('name, commission_percent').eq('id', policy['product_id']).execute()
                        if pr.data:
                            product_name = pr.data[0].get('name', '')
                            commission_percent = pr.data[0].get('commission_percent', 0) or 0
                    if policy.get('company_id'):
                        cr = self.supabase.table('companies').select('name').eq('id', policy['company_id']).execute()
                        if cr.data:
                            company_name = cr.data[0].get('name', '')
                    if policy.get('salesperson_id'):
                        sr = self.supabase.table('salespeople').select('name').eq('id', policy['salesperson_id']).execute()
                        if sr.data:
                            salesperson_name = sr.data[0].get('name', '')
                except Exception:
                    pass

                enriched.append((
                    policy.get('id'),
                    policy.get('end_date'),
                    policy.get('customer_name'),
                    policy.get('customer_tc_vkn'),
                    policy.get('plate'),
                    policy.get('doc_serial'),
                    policy.get('note'),
                    policy.get('premium'),
                    policy.get('product_id'),
                    product_name,
                    commission_percent,
                    policy.get('last_notified_on'),
                    policy.get('salesperson_id'),
                    salesperson_name,
                    policy.get('policy_number'),
                    policy.get('company_id'),
                    company_name
                ))
            return enriched
        except Exception as e:
            print(f"Error getting enriched policies: {e}")
            return []

    # Cross-selling methods
    def get_customers_for_cross_selling(self) -> List[Tuple]:
        """Get customers suitable for cross-selling"""
        try:
            result = self.supabase.table('policies').select('customer_name, customer_tc_vkn, product_id').execute()
            customers = []
            for policy in result.data:
                customers.append((
                    policy['customer_name'],
                    policy['customer_tc_vkn'],
                    policy['product_id']
                ))
            return customers
        except Exception as e:
            print(f"Error getting customers for cross-selling: {e}")
            return []

    def get_cross_selling_data(self, current_user: str = None) -> List[Tuple]:
        """Get cross-selling opportunities"""
        try:
            if current_user and self.is_user_admin(current_user):
                result = self.supabase.table('cross_selling').select('*').order('created_at', desc=True).execute()
            elif current_user:
                user_company_id = self.get_user_company_id(current_user)
                if user_company_id:
                    result = self.supabase.table('cross_selling').select('*').eq('company_id', user_company_id).order('created_at', desc=True).execute()
                else:
                    return []
            else:
                return []
            
            opportunities = []
            for opp in result.data:
                opportunities.append((
                    opp['id'],
                    opp['customer_name'],
                    opp['customer_tc_vkn'],
                    opp['phone'],
                    opp['email'],
                    opp['product_interest'],
                    opp['notes'],
                    opp['priority'],
                    opp['status'],
                    opp['created_at'],
                    opp['assigned_to'],
                    opp['company_id']
                ))
            return opportunities
        except Exception as e:
            print(f"Error getting cross-selling data: {e}")
            return []

    def get_cross_selling_opportunities(self, current_user: str = None) -> List[Tuple]:
        """Get cross-selling opportunities (alias for compatibility)"""
        return self.get_cross_selling_data(current_user)

    def add_cross_selling_opportunity(self, customer_name: str, customer_tc_vkn: str, phone: str, 
                                    email: str, product_interest: str, notes: str, priority: str, 
                                    assigned_to: int, company_id: int) -> bool:
        """Add cross-selling opportunity"""
        try:
            result = self.supabase.table('cross_selling').insert({
                'customer_name': customer_name,
                'customer_tc_vkn': customer_tc_vkn,
                'phone': phone,
                'email': email,
                'product_interest': product_interest,
                'notes': notes,
                'priority': priority,
                'status': 'new',
                'assigned_to': assigned_to,
                'company_id': company_id,
                'created_at': datetime.now().isoformat()
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error adding cross-selling opportunity: {e}")
            return False

    def update_cross_selling_status(self, opportunity_id: int, status: str) -> bool:
        """Update cross-selling opportunity status"""
        try:
            result = self.supabase.table('cross_selling').update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', opportunity_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating cross-selling status: {e}")
            return False

    def get_cross_selling_reminders(self) -> List[Tuple]:
        """Get cross-selling reminders"""
        try:
            result = self.supabase.table('cross_selling_reminders').select('*').order('reminder_date').execute()
            reminders = []
            for reminder in result.data:
                reminders.append((
                    reminder['id'],
                    reminder['cross_selling_id'],
                    reminder['reminder_date'],
                    reminder['reminder_type'],
                    reminder['notes'],
                    reminder['completed'],
                    reminder['created_at']
                ))
            return reminders
        except Exception as e:
            print(f"Error getting cross-selling reminders: {e}")
            return []

    def add_cross_selling_reminder(self, cross_selling_id: int, reminder_date: str, 
                                 reminder_type: str, notes: str) -> bool:
        """Add cross-selling reminder"""
        try:
            result = self.supabase.table('cross_selling_reminders').insert({
                'cross_selling_id': cross_selling_id,
                'reminder_date': reminder_date,
                'reminder_type': reminder_type,
                'notes': notes,
                'completed': False,
                'created_at': datetime.now().isoformat()
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error adding cross-selling reminder: {e}")
            return False

    def update_reminder_status(self, reminder_id: int, completed: bool) -> bool:
        """Update reminder completion status"""
        try:
            result = self.supabase.table('cross_selling_reminders').update({
                'completed': completed,
                'updated_at': datetime.now().isoformat()
            }).eq('id', reminder_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating reminder status: {e}")
            return False

    # Salespeople methods
    def get_all_salespeople(self, current_user: str = None) -> List[Tuple]:
        """Get all salespeople filtered by company"""
        try:
            if current_user and self.is_user_admin(current_user):
                result = self.supabase.table('salespeople').select('*').order('name').execute()
            elif current_user:
                user_company_id = self.get_user_company_id(current_user)
                if user_company_id:
                    result = self.supabase.table('salespeople').select('*').eq('company_id', user_company_id).order('name').execute()
                else:
                    return []
            else:
                return []
            
            salespeople = []
            for person in result.data:
                salespeople.append((
                    person['id'],
                    person['name'],
                    person['active'],
                    person['created_at'],
                    person['company_id']
                ))
            return salespeople
        except Exception as e:
            print(f"Error getting salespeople: {e}")
            return []

    def add_salesperson(self, name: str, company_id: int = None) -> bool:
        """Add a new salesperson"""
        try:
            result = self.supabase.table('salespeople').insert({
                'name': name,
                'active': True,
                'company_id': company_id,
                'created_at': datetime.now().isoformat()
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error adding salesperson: {e}")
            return False

    def get_salespeople_from_users(self, current_user: str = None) -> List[Tuple]:
        """Get users with salesperson role as salespeople"""
        try:
            # Satışçı rolü olan kullanıcıları bul (policies_add yetkisi olanlar)
            if current_user and self.is_user_admin(current_user):
                # Admin tüm satışçıları görebilir
                users_result = self.supabase.table('users').select('id, username, company_id').execute()
            elif current_user:
                # Normal kullanıcı sadece kendi şirketindeki satışçıları görebilir
                user_company_id = self.get_user_company_id(current_user)
                if user_company_id:
                    users_result = self.supabase.table('users').select('id, username, company_id').eq('company_id', user_company_id).execute()
                else:
                    return []
            else:
                return []
            
            salespeople = []
            for user in users_result.data:
                # Bu kullanıcının policies_add yetkisi var mı kontrol et
                if self.check_permission(user['username'], 'policies_add'):
                    salespeople.append((
                        user['id'],
                        user['username'],
                        True,  # active
                        None,  # created_at
                        user['company_id']
                    ))
            
            return salespeople
        except Exception as e:
            print(f"Error getting salespeople from users: {e}")
            return []

    def get_all_salespeople_combined(self, current_user: str = None) -> List[Tuple]:
        """Get salespeople from both users table and salespeople table"""
        try:
            all_salespeople = []
            
            # 1. Kullanıcı tablosundan satışçıları al (policies_add yetkisi olanlar)
            user_salespeople = self.get_salespeople_from_users(current_user)
            all_salespeople.extend(user_salespeople)
            
            # 2. Salespeople tablosundan da satışçıları al
            if current_user and self.is_user_admin(current_user):
                # Admin tüm satışçıları görebilir
                salespeople_result = self.supabase.table('salespeople').select('*').eq('active', True).execute()
            elif current_user:
                # Normal kullanıcı sadece kendi şirketindeki satışçıları görebilir
                user_company_id = self.get_user_company_id(current_user)
                if user_company_id:
                    salespeople_result = self.supabase.table('salespeople').select('*').eq('active', True).eq('company_id', user_company_id).execute()
                else:
                    salespeople_result = self.supabase.table('salespeople').select('*').eq('active', True).is_('company_id', 'null').execute()
            else:
                salespeople_result = self.supabase.table('salespeople').select('*').eq('active', True).execute()
            
            # Salespeople tablosundan gelen verileri ekle
            for sp in salespeople_result.data:
                # ID çakışmasını önlemek için salespeople tablosundan gelenlere 10000 ekle
                salespeople_id = sp['id'] + 10000
                all_salespeople.append((
                    salespeople_id,
                    sp['name'],
                    sp.get('active', True),
                    sp.get('created_at'),
                    sp.get('company_id')
                ))
            
            # Aynı isimli satışçıları filtrele (kullanıcı tablosundaki öncelikli)
            seen_names = set()
            unique_salespeople = []
            for sp in all_salespeople:
                name = sp[1]
                if name not in seen_names:
                    seen_names.add(name)
                    unique_salespeople.append(sp)
            
            return unique_salespeople
            
        except Exception as e:
            print(f"Error getting combined salespeople: {e}")
            return []

    def get_salespeople_only_from_table(self, current_user: str = None) -> List[Tuple]:
        """Get salespeople only from salespeople table (cleaner approach)"""
        try:
            # Sadece salespeople tablosundan satışçıları al
            if current_user and self.is_user_admin(current_user):
                # Admin tüm aktif satışçıları görebilir
                salespeople_result = self.supabase.table('salespeople').select('*').eq('active', True).order('name').execute()
            elif current_user:
                # Normal kullanıcı: company_id biliniyorsa sadece o şirketin satışçılarını göster
                user_company_id = self.get_user_company_id(current_user)
                if user_company_id:
                    salespeople_result = self.supabase.table('salespeople').select('*').eq('active', True).eq('company_id', user_company_id).order('name').execute()
                else:
                    # company_id yoksa hiç satışçı gösterme (güvenlik)
                    salespeople_result = self.supabase.table('salespeople').select('*').eq('active', True).eq('company_id', -999).order('name').execute()
            else:
                # Oturum yoksa tüm aktifleri göster (güvenli taraf)
                salespeople_result = self.supabase.table('salespeople').select('*').eq('active', True).order('name').execute()
            
            # Salespeople tablosundan gelen verileri formatla
            salespeople = []
            for sp in salespeople_result.data:
                salespeople.append((
                    sp['id'],
                    sp['name'],
                    sp.get('active', True),
                    sp.get('created_at'),
                    sp.get('company_id')
                ))
            
            return salespeople
            
        except Exception as e:
            print(f"Error getting salespeople from table: {e}")
            return []

    # Insurance companies methods
    def get_all_insurance_companies(self) -> List[Tuple]:
        """Get all insurance companies"""
        try:
            result = self.supabase.table('insurance_companies').select('*').order('name').execute()
            companies = []
            for company in result.data:
                companies.append((
                    company['id'],
                    company['name'],
                    company['active'],
                    company['created_at']
                ))
            return companies
        except Exception as e:
            print(f"Error getting insurance companies: {e}")
            return []

    # Customer methods for reports
    def get_all_customers(self) -> List[Tuple]:
        """Get all unique customers from policies"""
        try:
            result = self.supabase.table('policies').select('customer_name, customer_tc_vkn').execute()
            # Remove duplicates
            customers_set = set()
            for policy in result.data:
                customers_set.add((policy['customer_name'], policy['customer_tc_vkn']))
            return list(customers_set)
        except Exception as e:
            print(f"Error getting customers: {e}")
            return []

    def get_salespeople(self, current_user: str = None) -> List[Tuple]:
        """Get salespeople (alias for compatibility)"""
        return self.get_all_salespeople(current_user)

    def get_insurance_companies(self) -> List[Tuple]:
        """Get insurance companies (alias for compatibility)"""
        return self.get_all_insurance_companies()

    def get_policies(self, current_user: str = None) -> List[Tuple]:
        """Get policies (alias for compatibility)"""
        return self.get_all_policies(current_user)

    # Policy renewal methods
    def due_within_days(self, days: int) -> List[Tuple]:
        """Get policies due for renewal within specified days"""
        try:
            from datetime import datetime, timedelta
            today = datetime.now().date()
            end_date = (datetime.now() + timedelta(days=days)).date()
            
            result = self.supabase.table('policies').select('*').gte('end_date', today.isoformat()).lte('end_date', end_date.isoformat()).order('end_date').execute()
            
            policies = []
            for policy in result.data:
                # Get product and company names
                product_name = ""
                company_name = ""
                salesperson_name = ""
                
                try:
                    # Get product name
                    if policy['product_id']:
                        product_result = self.supabase.table('products').select('name').eq('id', policy['product_id']).execute()
                        if product_result.data:
                            product_name = product_result.data[0]['name']
                    
                    # Get company name
                    if policy['company_id']:
                        company_result = self.supabase.table('companies').select('name').eq('id', policy['company_id']).execute()
                        if company_result.data:
                            company_name = company_result.data[0]['name']
                    
                    # Get salesperson name
                    if policy['salesperson_id']:
                        salesperson_result = self.supabase.table('salespeople').select('name').eq('id', policy['salesperson_id']).execute()
                        if salesperson_result.data:
                            salesperson_name = salesperson_result.data[0]['name']
                except:
                    pass
                
                policies.append((
                    policy['id'],
                    policy['end_date'],
                    policy['customer_name'],
                    policy['customer_tc_vkn'],
                    policy['plate'],
                    policy['doc_serial'],
                    policy['note'],
                    policy['premium'],
                    policy['product_id'],
                    product_name,
                    policy.get('commission_percent', 0),
                    policy['last_notified_on'],
                    policy['salesperson_id'],
                    salesperson_name,
                    policy['policy_number'],
                    policy['company_id'],
                    company_name
                ))
            return policies
        except Exception as e:
            print(f"Error getting policies due within {days} days: {e}")
            return []

    def get_renewal_status(self, policy_id: int) -> Optional[str]:
        """Get renewal status for a policy"""
        try:
            result = self.supabase.table('renewal_status').select('status').eq('policy_id', policy_id).execute()
            return result.data[0]['status'] if result.data else None
        except Exception:
            return None

    def update_renewal_status(self, policy_id: int, status: str) -> bool:
        """Update renewal status for a policy"""
        try:
            # Try to update existing status
            existing = self.supabase.table('renewal_status').select('policy_id').eq('policy_id', policy_id).execute()
            
            if existing.data:
                result = self.supabase.table('renewal_status').update({
                    'status': status,
                    'updated_at': datetime.now().isoformat()
                }).eq('policy_id', policy_id).execute()
            else:
                result = self.supabase.table('renewal_status').insert({
                    'policy_id': policy_id,
                    'status': status,
                    'updated_at': datetime.now().isoformat()
                }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating renewal status: {e}")
            return False

    # Customer debt methods
    def get_customer_debts(self) -> List[Tuple]:
        """Get customer debt information from accounts"""
        try:
            result = self.supabase.table('accounts').select('*').order('transaction_date', desc=True).execute()
            debts = []
            for account in result.data:
                debts.append((
                    account['id'],
                    account['policy_id'],
                    account['transaction_type'],
                    account['amount'],
                    account['description'],
                    account['transaction_date'],
                    account['company_id']
                ))
            return debts
        except Exception as e:
            print(f"Error getting customer debts: {e}")
            return []

    def add_account_transaction(self, policy_id: int, transaction_type: str, amount: float, 
                              description: str, transaction_date: str, company_id: int) -> bool:
        """Add account transaction"""
        try:
            result = self.supabase.table('accounts').insert({
                'policy_id': policy_id,
                'transaction_type': transaction_type,
                'amount': amount,
                'description': description,
                'transaction_date': transaction_date,
                'company_id': company_id,
                'created_at': datetime.now().isoformat()
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error adding account transaction: {e}")
            return False

    def auto_generate_cross_selling_opportunities(self) -> int:
        """Otomatik olarak çapraz satış fırsatları oluştur."""
        try:
            now = datetime.now().isoformat()
            
            # Mevcut poliçeleri getir (son 60 gün içinde)
            policies_result = self.supabase.table('policies').select('''
                customer_name, customer_tc_vkn, product_id,
                products(name)
            ''').gte('end_date', (datetime.now() - timedelta(days=60)).date().isoformat()).execute()
            
            customers = {}
            for policy in policies_result.data:
                if policy['customer_name'] and policy['customer_name'].strip():
                    key = (policy['customer_name'], policy['customer_tc_vkn'])
                    if key not in customers:
                        customers[key] = {
                            'customer_name': policy['customer_name'],
                            'customer_tc_vkn': policy['customer_tc_vkn'],
                            'product_id': policy['product_id'],
                            'current_product': policy['products']['name'] if policy['products'] else None
                        }
            
            opportunities_created = 0
            
            for customer_data in customers.values():
                customer_name = customer_data['customer_name']
                customer_tc_vkn = customer_data['customer_tc_vkn']
                product_id = customer_data['product_id']
                current_product = customer_data['current_product']
                
                if not current_product:
                    continue
                
                # Bu müşteri için zaten çapraz satış fırsatı var mı kontrol et
                existing_result = self.supabase.table('cross_selling').select('id').eq('customer_name', customer_name).eq('customer_tc_vkn', customer_tc_vkn).execute()
                
                if existing_result.data:
                    continue  # Zaten fırsat var
                
                # Çapraz satış önerilerini al
                suggestions = self.get_cross_selling_suggestions(current_product)
                
                # Her öneri için fırsat oluştur
                for suggested_product in suggestions[:3]:  # En fazla 3 öneri
                    # Önerilen ürünün ID'sini bul
                    product_result = self.supabase.table('products').select('id').eq('name', suggested_product).execute()
                    
                    if product_result.data:
                        suggested_product_id = product_result.data[0]['id']
                        
                        # Öncelik belirle (ürün türüne göre)
                        priority = 2  # Orta öncelik
                        if suggested_product in ["FERDİ KAZA", "KONUT", "İŞYERİ"]:
                            priority = 3  # Yüksek öncelik
                        elif suggested_product in ["TSS", "FFL"]:
                            priority = 1  # Düşük öncelik
                        
                        # Fırsatı ekle
                        self.supabase.table('cross_selling').insert({
                            'customer_name': customer_name,
                            'customer_tc_vkn': customer_tc_vkn,
                            'current_product_id': product_id,
                            'suggested_product_id': suggested_product_id,
                            'priority': priority,
                            'status': 'pending',
                            'notes': f"Otomatik öneri: {current_product} → {suggested_product}",
                            'created_at': now,
                            'updated_at': now
                        }).execute()
                        
                        opportunities_created += 1
            
            return opportunities_created
            
        except Exception as e:
            print(f"Otomatik fırsat oluşturma hatası: {e}")
            return 0

    def get_companies(self) -> List[Tuple]:
        """Get all companies"""
        try:
            result = self.supabase.table('companies').select('*').order('name').execute()
            companies = []
            for company in result.data:
                companies.append((
                    company['id'],
                    company['name'],
                    company['created_at'],
                    company['active']
                ))
            return companies
        except Exception as e:
            print(f"Error getting companies: {e}")
            return []

    def get_user_count_by_company(self, company_id: int) -> int:
        """Get user count for a company"""
        try:
            result = self.supabase.table('users').select('id').eq('company_id', company_id).execute()
            return len(result.data)
        except Exception as e:
            print(f"Error getting user count: {e}")
            return 0

    def get_users_by_company(self, company_id: int) -> List[Tuple]:
        """Get all users for a company"""
        try:
            result = self.supabase.table('users').select('id, username, is_admin, created_at, last_login').eq('company_id', company_id).order('username').execute()
            users = []
            for user in result.data:
                users.append((
                    user['id'],
                    user['username'],
                    user['is_admin'],
                    user['created_at'],
                    user['last_login']
                ))
            return users
        except Exception as e:
            print(f"Error getting users by company: {e}")
            return []

    def get_company_name(self, company_id: int) -> str:
        """Get company name by ID"""
        try:
            result = self.supabase.table('companies').select('name').eq('id', company_id).execute()
            if result.data:
                return result.data[0]['name']
            return ""
        except Exception as e:
            print(f"Error getting company name: {e}")
            return ""

    def get_products(self) -> List[Tuple]:
        """Get all products (basic version)"""
        try:
            result = self.supabase.table('products').select('*').order('name').execute()
            products = []
            for product in result.data:
                products.append((
                    product['id'],
                    product['name'],
                    product.get('commission_percent', 15.0)
                ))
            return products
        except Exception as e:
            print(f"Error getting products: {e}")
            return []

    def add_product(self, name: str, commission_percent: float) -> bool:
        """Add a new product (basic version)"""
        try:
            now = datetime.now().isoformat()
            result = self.supabase.table('products').insert({
                'name': name,
                'commission_percent': commission_percent,
                'created_at': now,
                'updated_at': now
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error adding product: {e}")
            return False

    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        try:
            result = self.supabase.table('products').delete().eq('id', product_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False

    def delete_all_products(self) -> bool:
        """Delete all products from the database"""
        try:
            # Get all products first
            all_products = self.supabase.table('products').select('id').execute()
            if all_products.data:
                # Delete all products
                result = self.supabase.table('products').delete().neq('id', 0).execute()
                print(f"Deleted {len(all_products.data)} products")
                return True
            else:
                print("No products found to delete")
                return True
        except Exception as e:
            print(f"Error deleting all products: {e}")
            return False

    def update_product(self, product_id: int, name: str, commission_percent: float) -> bool:
        """Update a product (basic version)"""
        try:
            now = datetime.now().isoformat()
            result = self.supabase.table('products').update({
                'name': name,
                'commission_percent': commission_percent,
                'updated_at': now
            }).eq('id', product_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating product: {e}")
            return False

    def get_products_enhanced(self) -> List[Tuple]:
        """Get all products with enhanced information"""
        try:
            result = self.supabase.table('products').select('*').order('name').execute()
            products = []
            for product in result.data:
                products.append((
                    product['id'],
                    product['name'],
                    product.get('commission_percent', 15.0),
                    product.get('category', ''),
                    product.get('active', True),
                    product.get('description', ''),
                    product.get('created_at', ''),
                    product.get('updated_at', '')
                ))
            return products
        except Exception as e:
            print(f"Error getting enhanced products: {e}")
            return []

    def add_product_enhanced(self, name: str, commission_percent: float, category: str = "", active: bool = True, description: str = "") -> bool:
        """Add a new product with enhanced information"""
        try:
            now = datetime.now().isoformat()
            result = self.supabase.table('products').insert({
                'name': name,
                'commission_percent': commission_percent,
                'category': category,
                'active': active,
                'description': description,
                'created_at': now,
                'updated_at': now
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error adding enhanced product: {e}")
            return False

    def update_product_enhanced(self, product_id: int, name: str, commission_percent: float, category: str = "", active: bool = True, description: str = "") -> bool:
        """Update a product with enhanced information"""
        try:
            now = datetime.now().isoformat()
            result = self.supabase.table('products').update({
                'name': name,
                'commission_percent': commission_percent,
                'category': category,
                'active': active,
                'description': description,
                'updated_at': now
            }).eq('id', product_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating enhanced product: {e}")
            return False

    def get_cross_selling_suggestions(self, current_product: str) -> List[str]:
        """Mevcut ürüne göre çapraz satış önerileri getir."""
        suggestions_map = {
            "TRAFİK": ["KASKO", "FERDİ KAZA", "KONUT"],
            "KASKO": ["TRAFİK", "FERDİ KAZA", "KONUT"],
            "DASK": ["KONUT", "YANGIN", "İŞYERİ"],
            "KONUT": ["DASK", "YANGIN", "FERDİ KAZA"],
            "İŞYERİ": ["KONUT", "YANGIN", "FERDİ KAZA"],
            "YANGIN": ["KONUT", "İŞYERİ", "DASK"],
            "NAKLİYAT": ["İŞYERİ", "FERDİ KAZA", "TRAFİK"],
            "FERDİ KAZA": ["KONUT", "KASKO", "TAMAMLAYICI SAĞLIK"],
            "TAMAMLAYICI SAĞLIK": ["ÖZEL SAĞLIK", "FERDİ KAZA", "KONUT"],
            "ÖZEL SAĞLIK": ["TAMAMLAYICI SAĞLIK", "FERDİ KAZA", "KONUT"]
        }
        
        return suggestions_map.get(current_product, ["FERDİ KAZA", "KONUT", "KASKO"])

    # Test connection
    def overdue(self) -> List[Tuple]:
        """Get policies that are overdue for renewal"""
        try:
            from datetime import datetime
            today = datetime.now().date()
            
            result = self.supabase.table('policies').select('*').lt('end_date', today.isoformat()).order('end_date').execute()
            
            policies = []
            for policy in result.data:
                # Get product and company names
                product_name = ""
                company_name = ""
                salesperson_name = ""
                
                try:
                    # Get product name
                    if policy['product_id']:
                        product_result = self.supabase.table('products').select('name').eq('id', policy['product_id']).execute()
                        if product_result.data:
                            product_name = product_result.data[0]['name']
                    
                    # Get company name
                    if policy['company_id']:
                        company_result = self.supabase.table('companies').select('name').eq('id', policy['company_id']).execute()
                        if company_result.data:
                            company_name = company_result.data[0]['name']
                    
                    # Get salesperson name
                    if policy['salesperson_id']:
                        salesperson_result = self.supabase.table('salespeople').select('name').eq('id', policy['salesperson_id']).execute()
                        if salesperson_result.data:
                            salesperson_name = salesperson_result.data[0]['name']
                except:
                    pass
                
                policies.append((
                    policy['id'],
                    policy['end_date'],
                    policy['customer_name'],
                    policy['customer_tc_vkn'],
                    policy['plate'],
                    policy['doc_serial'],
                    policy['note'],
                    policy['premium'],
                    policy['product_id'],
                    product_name,
                    policy.get('commission_percent', 0),
                    policy['last_notified_on'],
                    policy['salesperson_id'],
                    salesperson_name,
                    policy['policy_number'],
                    policy['company_id'],
                    company_name
                ))
            return policies
        except Exception as e:
            print(f"Error getting overdue policies: {e}")
            return []

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            result = self.supabase.table('companies').select('*').limit(1).execute()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
