// Tipos compartidos del dominio VoltGrid.

export type Role = 'superadmin' | 'org_admin' | 'operator' | 'viewer';

export type StationStatus =
  | 'available'
  | 'occupied'
  | 'offline'
  | 'maintenance';

export interface User {
  id: string;
  email: string;
  role: Role;
  org_id: string;
}

export interface Org {
  id: string;
  name: string;
  slug: string;
  domain: string | null;
  logo_url: string | null;
  primary_color: string | null;
}

export interface Station {
  id: string;
  name: string;
  location: string;
  lat: number | null;
  lng: number | null;
  max_kw: number;
  status: StationStatus;
  org_id: string;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Payload para crear una estación (operator+).
export interface StationCreate {
  name: string;
  location: string;
  lat?: number | null;
  lng?: number | null;
  max_kw: number;
  status?: StationStatus;
}

// Payload para actualizar una estación (operator+).
export interface StationUpdate {
  name?: string;
  location?: string;
  lat?: number | null;
  lng?: number | null;
  max_kw?: number;
}

export interface SchedulerConfig {
  enabled: boolean;
  interval_minutes: number;
}

export interface StationKPI {
  station_id: string;
  name: string;
  uptime_pct: number;
  kwh_delivered: number;
  active_sessions: number;
}

export interface KPISummary {
  total_stations: number;
  total_kwh: number;
  active_sessions: number;
  avg_uptime_pct: number;
  stations: StationKPI[];
}

// Filtros de la vista de analítica.
export interface AnalyticsFilters {
  date_from?: string;
  date_to?: string;
  location?: string;
  min_capacity?: string;
  max_capacity?: string;
  status?: StationStatus | '';
}

// Mensaje recibido por WebSocket al cambiar el estado de una estación.
export interface StationStatusMessage {
  station_id: string;
  status: StationStatus;
  old_status: StationStatus;
  source: string;
  timestamp: string;
}

// Whitelabel: actualización parcial de la organización (org_admin).
export interface OrgUpdate {
  name?: string;
  logo_url?: string;
  primary_color?: string;
}
