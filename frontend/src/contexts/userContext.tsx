import { createContext } from "react";

export interface User {
    id: string;
    email: string;
    token: string;
    first_name: string;
    last_name: string;
}

interface UserContextType {
    user: User | null;
    setUser: (user: User | null) => void;
}

export const UserContext = createContext<UserContextType | undefined>(undefined);
