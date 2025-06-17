import { Link } from '@tanstack/react-router'
import { useUserContext } from '@/contexts/userContext';

export default function Header() {

  const { user } = useUserContext();

  return (
    <header className="flex justify-center items-center py-8 gap-2">
      <nav className="flex flex-row">
        <div className="px-2 font-bold">
          <Link to="/">Home</Link>
        </div>
        {user
          ?
          <div className="px-2 font-bold">
            <Link to="/profile">Profile</Link>
          </div>
          :
          <>
            <div className="px-2 font-bold">
              <Link to="/login">Login</Link>
            </div>
            <div className="px-2 font-bold">
              <Link to="/register">Register</Link>
            </div>
          </>
        }
      </nav>
    </header>
  )
}
