export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string | null;
  last_name: string | null;
  verified: boolean;
}

export interface UserRegister {
  email: string;
  password: string;
  username: string;
  first_name: string;
  last_name: string;
}