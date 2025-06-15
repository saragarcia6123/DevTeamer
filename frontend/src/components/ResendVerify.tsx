import { useState } from "react";
import { resendVerification } from "@/api/fetch";
import { HTTPError } from "@/api/http_error";

export default function ResendVerify({ email }: { email: string | null }) {
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

    return <>
        {resentMessage
            ? (<p className="break-all">{resentMessage}</p>)
            : email
                ? (<p onClick={requestResend} className="hover:cursor-pointer underline">Resend verification email</p>)
                : null}
    </>
}