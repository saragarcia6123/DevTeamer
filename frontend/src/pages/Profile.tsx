import React, { useContext } from "react";
import { UserContext } from "../contexts/userContext";

const Profile: React.FC = () => {
  const context = useContext(UserContext);

  if (!context) {
    throw new Error("Profile must be used within a UserContext.Provider");
  }

  const { user } = context;

  if (!user) {
    return <p>Please log in to see your profile.</p>;
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded shadow mt-8">
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      <p><strong>ID:</strong> {user.id}</p>
      <p><strong>Email:</strong> {user.email}</p>
      <p><strong>First Name:</strong> {user.first_name}</p>
      <p><strong>Last Name:</strong> {user.last_name}</p>
    </div>
  );
};

export default Profile;
