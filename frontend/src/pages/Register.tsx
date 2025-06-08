import { useRef, useState } from "react";
import { useSearch } from "@tanstack/react-router";
import type { UserRegister } from "@/models/User";
import { register } from "@/auth";

function RegisterSuccessCard({ email }: { email: string }) {
    return (
        <div className="form-info text-green-900 border-green-900">
            <h2>Registration Successful!</h2>
            <p>
                A verification email has been sent to <strong>{email}</strong>.
            </p>
            <p>Please check your inbox and follow the instructions to verify your account.</p>
        </div>
    );
}

export default function Register() {
    const search = useSearch({ from: "/register" });

    const email = search.email ?? null;

    const emailRef = useRef<HTMLInputElement>(null);
    const usernameRef = useRef<HTMLInputElement>(null);
    const firstNameRef = useRef<HTMLInputElement>(null);
    const lastNameRef = useRef<HTMLInputElement>(null);
    const passwordRef = useRef<HTMLInputElement>(null);
    const repeatPasswordRef = useRef<HTMLInputElement>(null);

    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        setError(null);
        setSuccess(false);
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

        try {
            await register(payload);
            setSuccess(true);
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
            {
                success
                    ? <RegisterSuccessCard email={email || ""} /> :
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
            }
        </div>
    );
}
