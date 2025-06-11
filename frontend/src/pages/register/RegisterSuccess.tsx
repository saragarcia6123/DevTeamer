import ResendVerify from "@/components/ResendVerify";

export default function RegisterSuccess() {
    const params = new URLSearchParams(location.search);
    const email = params.get("email");

    return (
        <div className="flex items-center align-middle">
            <div className="form-info">
                <h2>Registration Successful!</h2>
                <p>
                    A verification email has been sent to {email ? <strong>{email}</strong> : "your email"}.
                </p>
                <p>Please check your inbox and follow the instructions to verify your account.</p>
                <ResendVerify email={email}/>
            </div>
        </div>
    );
}