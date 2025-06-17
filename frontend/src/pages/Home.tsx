import { useUserContext } from "@/contexts/userContext";

export default function Home() {

  const { user } = useUserContext();

  return (
    <div className="w-full flex justify-center items-center text-2xl">
      Welcome to DevTeamer{user ? `, ${user.first_name}` : ""}!
    </div>
  );
}
