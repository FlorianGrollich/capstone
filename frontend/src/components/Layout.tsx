import {useState} from "react";
import {Link, Outlet} from "react-router-dom";
import {X} from "lucide-react";
import {useDispatch} from "react-redux";
import {AppDispatch} from "../store.ts";
import {logout} from "../features/Auth/slices/authState.ts";
import Auth from "./Auth.tsx";

const Layout = () => {
    const [isOpen, setIsOpen] = useState(false);
    const dispatch = useDispatch<AppDispatch>();

    return (
        <div className="flex h-screen">
            <Auth/>
            <div
                className={`fixed inset-y-0 left-0 w-64 bg-primary text-white transform ${isOpen ? "translate-x-0" : "-translate-x-full"} transition-transform duration-300 ease-in-out md:relative md:translate-x-0`}>
                <div className="p-4 flex justify-between items-center">
                    <h1 className="text-xl font-bold">MyApp</h1>
                    <button className="md:hidden" onClick={() => setIsOpen(false)}>
                        <X className="h-6 w-6"/>
                    </button>
                </div>
                <nav className="mt-4">
                    <Link to="/" className="block py-2 px-4 hover:bg-gray-700">Home</Link>
                    <Link to="/login" onClick={() => dispatch(logout())}
                          className="block py-2 px-4 hover:bg-gray-700">Logout</Link>
                </nav>
            </div>


            <div className="flex-1 flex flex-col">
                <header className="p-4 flex justify-between items-center">
                    <h1 className="text-3xl font-bold">Dashboard</h1>
                </header>
                <main className="p-4 flex-1">
                    <Outlet/>
                </main>
            </div>
        </div>
    );
};

export default Layout;
