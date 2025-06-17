import Header from "./components/Header";
import Footer from "./components/Footer";
import { UserProvider } from "./contexts/userProvider";
import type { ReactNode } from "react";

export default function Scaffold({ children }: { children: ReactNode }) {

    return <UserProvider>
        <div className="min-h-screen flex flex-col">
            <Header />
            <main>{children}</main>
            <Footer />
        </div>
    </UserProvider>
}