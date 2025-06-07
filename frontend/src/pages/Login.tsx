import {  useContext, useRef } from "react";
import {  UserContext } from "@/contexts/userContext";

export default function Login() {

    const emailInput = useRef<HTMLInputElement>(null);
    const passwordInput = useRef<HTMLInputElement>(null);

    const context = useContext(UserContext);
    if (!context) throw new Error("useContext must be within UserProvider");

    async function submit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        const email = emailInput.current?.value;
        const password = passwordInput.current?.value;

        if (!email) {
            console.error("Email is missing");
            emailInput.current!.style.borderColor = 'red';
            return;
        }

        if (!password) {
            console.error("Password is missing");
            passwordInput.current!.style.borderColor = 'red';
            return;
        }

        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const API_URL = import.meta.env.VITE_API_URL;

        try {
            const response = await fetch(`${API_URL}/auth`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData.toString(),
                credentials: "include"
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || "Login error");
            }

            const responseJson = await response.json();
            console.log(responseJson);

            const userResponse = await fetch(`${API_URL}/users/me`, {
                method: "GET",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
            });

            if (!userResponse.ok) {
                console.error("Failed to fetch user");
                return;
            }

            const userData = await userResponse.json();
            context!.setUser(userData);

        } catch (err) {
            console.error("Login error:", err);
        }
    }

    return (
  <div className="flex justify-center items-center min-h-[400px] bg-gray-100">
    <form 
      onSubmit={submit} 
      className="bg-white p-8 rounded-lg shadow-md w-full max-w-md flex flex-col gap-6"
    >
      <input
        type="email"
        name="email"
        ref={emailInput}
        placeholder="Email"
        className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        required
      />
      <input
        type="password"
        name="password"
        ref={passwordInput}
        placeholder="Password"
        className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        required
      />
      <button
        type="submit"
        className="bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 transition-colors"
      >
        Login
      </button>
    </form>
  </div>
);

}