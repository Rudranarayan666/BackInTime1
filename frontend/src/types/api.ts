export interface Health {
  status: string;
  version: string;
}

export interface SystemInfo {
  platform: string;
  python_version: string;
  rsync_available: boolean;
}

export interface Profile {
  profile_id: string;
  name: string;
  sources: string[];
  target: string;
  excludes: string[];
}

export interface ProfileList {
  profiles: Profile[];
}

export interface ApiErrorResponse {
  error?: {
    code?: string;
    message?: string;
    request_id?: string;
  };
  detail?: unknown;
}
