import { Link } from "react-router-dom";

const Layout = () => {

    return (
        <div className="flex h-screen">
            <div className={`fixed inset-y-0 left-0 w-64 bg-primary text-white `}>
                <div className="p-4 flex justify-between items-center">
                    <h1 className="text-xl font-bold">MyApp</h1>
                </div>
                <nav className="mt-4">
                    <Link to="/" className="block py-2 px-4 hover:bg-gray-700">Home</Link>
                </nav>
            </div>



        </div>
    );
};

export default Layout;
