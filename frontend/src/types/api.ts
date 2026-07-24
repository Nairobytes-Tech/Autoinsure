export interface PaginatedResponse<T> {
  pagination: {
    count: number;
    total_pages: number;
    current_page: number;
    page_size: number;
    next: string | null;
    previous: string | null;
  };
  results: T[];
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}

export interface Tenant {
  id: string;
  name: string;
  code: string;
  slug: string;
  tier: string;
  logo: string | null;
  website: string;
  email: string;
  phone: string;
  city: string;
  state: string;
  country: string;
  is_active: boolean;
  currency: string;
  timezone: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone_number: string;
  avatar: string | null;
  role: string;
  tenant: string | null;
  branch: string | null;
  is_active: boolean;
  is_platform_admin: boolean;
  mfa_enabled: boolean;
  date_joined: string;
  last_login: string;
}

export interface Customer {
  id: string;
  tenant: string;
  title: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  date_of_birth: string | null;
  gender: string;
  national_id_number: string | null;
  city: string;
  state: string;
  country: string;
  status: string;
  source: string;
  active_policies_count: number;
  total_premium_paid: number;
  created_at: string;
  updated_at: string;
}

export interface Policy {
  id: string;
  tenant: string;
  customer: string;
  customer_name?: string;
  product: string;
  product_name?: string;
  policy_number: string;
  policy_type: string;
  policy_status: string;
  payment_status: string;
  start_date: string;
  end_date: string;
  premium_amount: number;
  sum_insured: number;
  tax_amount: number;
  net_premium: number;
  currency: string;
  agent: string | null;
  broker: string | null;
  branch: string | null;
  created_at: string;
  updated_at: string;
}

export interface Claim {
  id: string;
  tenant: string;
  policy: string;
  policy_number?: string;
  claim_number: string;
  claim_status: string;
  claim_type: string;
  priority: string;
  incident_date: string;
  reported_date: string;
  claim_amount: number;
  approved_amount: number;
  paid_amount: number;
  customer: string;
  customer_name?: string;
  assigned_to: string | null;
  fraud_flag: boolean;
  created_at: string;
  updated_at: string;
}

export interface Quote {
  id: string;
  tenant: string;
  customer: string;
  customer_name?: string;
  product: string;
  product_name?: string;
  quote_number: string;
  quote_status: string;
  valid_until: string;
  premium_amount: number;
  sum_insured: number;
  net_premium: number;
  currency: string;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: string;
  tenant: string;
  reference_number: string;
  payment_for: string;
  payment_status: string;
  amount: number;
  paid_amount: number;
  currency: string;
  payer_name: string;
  payment_date: string;
  created_at: string;
}

export interface Product {
  id: string;
  tenant: string;
  category: string;
  name: string;
  code: string;
  product_type: string;
  billing_frequency: string;
  base_premium: number;
  minimum_premium: number;
  maximum_premium: number;
  status: string;
  is_renewable: boolean;
  is_featured: boolean;
  created_at: string;
}

export interface Agent {
  id: string;
  tenant: string;
  agent_code: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  branch: string | null;
  commission_rate: number;
  target_premium: number;
  achieved_premium: number;
  total_policies_sold: number;
  status: string;
  created_at: string;
}

export interface Broker {
  id: string;
  tenant: string;
  broker_code: string;
  company_name: string;
  contact_person: string;
  email: string;
  phone: string;
  commission_rate: number;
  total_premium_placed: number;
  total_policies_sold: number;
  status: string;
  created_at: string;
}

export interface Dealer {
  id: string;
  tenant: string;
  dealer_code: string;
  company_name: string;
  contact_person: string;
  email: string;
  phone: string;
  dealer_type: string;
  total_policies_sold: number;
  status: string;
  created_at: string;
}

export interface Branch {
  id: string;
  tenant: string;
  name: string;
  code: string;
  branch_type: string;
  city: string;
  state: string;
  total_policies: number;
  total_customers: number;
  target_premium: number;
  achieved_premium: number;
  status: string;
  created_at: string;
}

export interface AuditLog {
  id: string;
  tenant: string;
  user: string | null;
  user_email?: string;
  action_type: string;
  entity_type: string;
  entity_id: string | null;
  entity_name: string;
  description: string;
  ip_address: string;
  request_method: string;
  request_path: string;
  response_status: number;
  duration_ms: number;
  is_success: boolean;
  created_at: string;
}

export interface Notification {
  id: string;
  tenant: string;
  recipient: string;
  notification_type: string;
  channel: string;
  priority: string;
  subject: string;
  message: string;
  is_read: boolean;
  read_at: string | null;
  is_sent: boolean;
  created_at: string;
}

export interface DashboardStats {
  total_policies: number;
  active_policies: number;
  total_claims: number;
  pending_claims: number;
  total_customers: number;
  total_revenue: number;
  total_premium: number;
  pending_payments: number;
}
