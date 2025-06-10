export default function ConfirmLogin() {
    const params = new URLSearchParams(location.search);
    const email = params.get("email");

    return (
        <div className="flex items-center align-middle">
            <div className="form-info">
                <p>
                    An email has been sent to {email ? <strong>{email}</strong> : "your email"}.
                </p>
                <p>Please check your inbox and follow the instructions to login.</p>
            </div>
        </div>
    );
}