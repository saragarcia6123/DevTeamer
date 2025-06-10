import { useRef, useState } from "react";
import { useNavigate, useSearch } from "@tanstack/react-router";
import type { UserRegister } from "@/models/User";
import { register } from "@/api";


export default function Register() {
    const search = useSearch({ from: "/register" });
    const navigate = useNavigate();

    // For handing over email when coming from login
    const email = search.email ?? null;

    // Use refs for safety
    const emailRef = useRef<HTMLInputElement>(null);
    const usernameRef = useRef<HTMLInputElement>(null);
    const firstNameRef = useRef<HTMLInputElement>(null);
    const lastNameRef = useRef<HTMLInputElement>(null);
    const passwordRef = useRef<HTMLInputElement>(null);
    const repeatPasswordRef = useRef<HTMLInputElement>(null);

    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        setError(null);
        setLoading(true);

        if (passwordRef.current?.value !== repeatPasswordRef.current?.value) {
            setError("Passwords do not match.");
            setLoading(false);
            return;
        }

        const payload: UserRegister = {
            email: emailRef.current?.value || "",
            username: usernameRef.current?.value || "",
            first_name: firstNameRef.current?.value || "",
            last_name: lastNameRef.current?.value || "",
            password: passwordRef.current?.value || "",
        };

        if (import.meta.env.DEV) {
            console.log(payload);
        }

        try {
            await register(payload);
            navigate({ to: `/register-success?email=${emailRef.current?.value}` })
        } catch (err) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError(String(err));
            }
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="flex justify-center items-center w-full py-8">
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    name="email"
                    ref={emailRef}
                    defaultValue={email || ""}
                    placeholder="Email"
                    required
                />
                <input
                    type="text"
                    name="username"
                    ref={usernameRef}
                    placeholder="Username"
                    required
                />
                <div className="flex gap-2">
                    <input
                        type="text"
                        name="firstName"
                        ref={firstNameRef}
                        placeholder="First Name"
                        required
                    />
                    <input
                        type="text"
                        name="lastName"
                        ref={lastNameRef}
                        placeholder="Last Name"
                    />
                </div>
                <input
                    type="password"
                    name="password"
                    ref={passwordRef}
                    placeholder="Password"
                    required
                />

                <input
                    type="password"
                    name="password-repeat"
                    ref={repeatPasswordRef}
                    placeholder="Repeat Password"
                    required
                />
                {error && <p className="text-red-600 text-sm">{error}</p>}

                <button
                    type="submit"
                    disabled={loading}
                >
                    {loading ? "Registering..." : "Register"}
                </button>
            </form>
        </div>
    );
}
