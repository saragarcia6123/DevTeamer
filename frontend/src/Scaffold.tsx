import { useEffect } from "react";
import Header from "./components/Header";
import Footer from "./components/Footer";
import { useUserContext } from "./contexts/userContext";
import { fetchCurrentUser } from "./auth";
import type { ReactNode } from "react";

export default function Scaffold({ children }: { children: ReactNode }) {

    const { user } = useUserContext();

    useEffect(() => {
        // Fetch user details if logged in
        if (user) {
            fetchCurrentUser();
        }
    }, [user]);

    return <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex flex-1 justify-center align-middle">
            {children}
        </main>
        <Footer />
    </div>
}