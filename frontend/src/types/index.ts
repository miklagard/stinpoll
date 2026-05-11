export interface UserRegistration {
  email: string;
  password: string;
  username: string;
}

export interface ProfilePhoto {
  id?: string;
  photo: string;
  is_primary: boolean;
  order: number;
}

export interface Profile {
  id?: string;
  eksisozluk_username: string;
  photos?: ProfilePhoto[];
  age: number;
  marital_status: 'bekar' | 'bosanmis' | 'dul' | '';
  has_children: boolean;
  city: string;
  religious_view: number;
}

export interface ProfileFormData extends Profile {
  uploaded_photos: File[];
}

export interface VerificationResponse {
  message: string;
  error?: string;
  token?: string;
  user_id?: string;
  email?: string;
}

export interface LoginResponse {
  token: string;
  user_id: string;
  email: string;
}