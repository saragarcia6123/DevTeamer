import Header from "./components/Header";
import Footer from "./components/Footer";
import { UserProvider } from "./contexts/userProvider";
import type { ReactNode } from "react";

export default function Scaffold({ children }: { children: ReactNode }) {

    return <UserProvider>
        <div className="min-h-screen flex flex-col">
            <Header />
            <main className="flex flex-1 justify-center align-middle size-full p-8 md:p-0">
                {children}
            </main>
            <Footer />
        </div>
    </UserProvider>
}