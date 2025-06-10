import { useState } from "react";
import { HTTPError, resendVerification } from "@/api";

export default function RegisterSuccess() {
    const params = new URLSearchParams(location.search);
    const email = params.get("email");

    const [resentMessage, setResentMessage] = useState<string | null>(null);

    async function requestResend() {
        try {
            const msg: string = await resendVerification(email!);
            setResentMessage(msg);
        } catch (err) {
            if (err instanceof HTTPError) {
                setResentMessage(err.message);
            } else {
                setResentMessage("Failed to request email.");
            }
        }
    }

    return (
        <div className="flex items-center align-middle">
            <div className="form-info">
                <h2>Registration Successful!</h2>
                <p>
                    A verification email has been sent to {email ? <strong>{email}</strong> : "your email"}.
                </p>
                <p>Please check your inbox and follow the instructions to verify your account.</p>
                {resentMessage ? (
                    <p>{resentMessage}</p>
                ) : email ? (
                    <p onClick={requestResend}>Resend email</p>
                ) : null}
            </div>
        </div>
    );
}