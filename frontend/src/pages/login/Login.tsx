import { useContext, useEffect, useRef, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import z from "zod";
import { UserContext, useUserContext } from "@/contexts/userContext";
import { HTTPError, login, userExists } from "@/api";
import ResendVerify from "@/components/ResendVerify";

export default function Login() {

  const { user } = useUserContext();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate({ to: "/profile" });
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

    const email = emailInput.current?.value;

    if (!email) {
      emailInput.current!.style.borderColor = "red";
      return;
    }

    if (!z.string().email().safeParse(email).success) {
      emailInput.current!.style.borderColor = "red";
      return;
    }

    const exists = await userExists(email);
    if (exists) {
      setStep("password");
    } else {
      navigate({ to: "/register", search: { email } });
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
      navigate({ to: `/confirm-login?email=${email}` })
    } catch (err) {
      if (err instanceof HTTPError) {
        setError(err.message);
        if (err.statusCode === 403) {
          setUnverified(true)
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
        {unverified && <ResendVerify email={emailInput.current!.value}/>}
        <button
          type="submit"
        >
          {step === "email" ? "Next" : "Login"}
        </button>
      </form>
    </div>
  );
}
