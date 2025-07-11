import { useContext, useEffect, useRef, useState } from "react";
import { useNavigate, useSearch } from "@tanstack/react-router";
import z from "zod";
import { UserContext, useUserContext } from "@/contexts/userContext";
import ResendVerify from "@/components/ResendVerify";
import { HTTPError } from "@/api/http_error";
import { login } from "@/api/routes/auth";
import { userExists, userVerified } from "@/api/routes/users";
import { ROUTES } from "@/routes";

export default function Login() {

  const { user } = useUserContext();
  const navigate = useNavigate();

  const search = useSearch({ from: ROUTES.login });
  const qEmail = search.email ?? null;

  useEffect(() => {
    if (user) {
      navigate({ to: ROUTES.profile });
    }
  }, [user, navigate]);

  const emailInput = useRef<HTMLInputElement>(null);
  const passwordInput = useRef<HTMLInputElement>(null);

  const context = useContext(UserContext);
  if (!context) throw new Error("useContext must be within UserProvider");

  const [step, setStep] = useState<"email" | "password">("email");
  const [error, setError] = useState<string | null>(null);
  const [unverified, setUnverified] = useState<boolean>(false);

  async function handleEmailSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    setError(null);

    const email = emailInput.current?.value;

    if (!email) {
      emailInput.current!.style.borderColor = "red";
      return;
    }

    if (!z.string().email().safeParse(email).success) {
      emailInput.current!.style.borderColor = "red";
      return;
    }

    let exists = false;

    try {
      exists = await userExists(email);
      if (exists) {
        setStep("password");
      } else {
        navigate({
          to: ROUTES.register,
          search: { email: email }
        });
      }
    } catch (err: any) {
      if (err instanceof HTTPError) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    }

  }

  async function handlePasswordSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const email = emailInput.current?.value;
    const password = passwordInput.current?.value;

    if (!password) {
      if (passwordInput.current) {
        passwordInput.current.style.borderColor = "red";
      }
      return;
    }

    try {
      await login(email!, password);
      navigate({ to: `${ROUTES.confirmLogin}?email=${email}` })
    } catch (err) {
      if (err instanceof HTTPError) {
        const verified = await userVerified(email!);
        if (!verified) {
          setUnverified(true)
        } else {
          setError(err.message);
        }
      } else {
        setError(String(err));
      }
    }
  }


  return (
    <div className="flex flex-col justify-center items-center w-full">
      <form onSubmit={step === "email" ? handleEmailSubmit : handlePasswordSubmit}>
        <input
          type="string"
          name="email"
          ref={emailInput}
          placeholder="Email"
          defaultValue={qEmail || ""}
          required
        />
        {step === "password" && (
          <input
            type="password"
            name="password"
            ref={passwordInput}
            placeholder="Password"
            required
          />
        )}
        {error && <p className="text-red-600 text-sm">{error}</p>}
        {unverified && <ResendVerify email={emailInput.current!.value} />}
        <button
          type="submit"
        >
          {step === "email" ? "Next" : "Login"}
        </button>
      </form>
    </div>
  );
}
