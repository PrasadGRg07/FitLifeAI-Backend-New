import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';

const NAV_ITEMS = [
    { label: 'Home', to: '/' },
    { label: 'About', to: '/aboutus' },
    { label: 'Features', to: '/features' },
    { label: 'Plans', to: '/plans' },
    { label: 'Products', to: '/products' },
    { label: 'Cart', to: '/cart' },
];

function Navbar() {
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);

    const linkClass = ({ isActive }) =>
        `text-sm font-medium tracking-wide transition-colors duration-200 ${
            isActive
                ? 'text-emerald-600 font-semibold'
                : 'text-gray-700 hover:text-emerald-600'
        }`;

    const goTo = (path) => {
        setOpen(false);
        navigate(path);
    };

    return (
        <header className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100 shadow-sm">
            <nav className="max-w-6xl mx-auto flex items-center justify-between px-4 sm:px-6 h-16">
                <Link to="/" className="flex items-center gap-2" aria-label="FitLife AI Home">
                    <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.5 21v-1.5a4.5 4.5 0 014.5-4.5h.75M20.25 21v-1.5a5.25 5.25 0 00-5.25-5.25M13 10.5h5.25" />
                        </svg>
                    </span>
                    <span className="text-xl font-extrabold tracking-tight text-gray-900">
                        FitLife<span className="text-emerald-600">AI</span>
                    </span>
                </Link>

                <div className="hidden md:flex items-center gap-7">
                    {NAV_ITEMS.map((item) => (
                        <NavLink key={item.to} to={item.to} end={item.to === '/'} className={linkClass}>
                            {item.label}
                        </NavLink>
                    ))}
                </div>

                <div className="hidden md:flex items-center gap-4">
                    <Link to="/login" className="text-sm font-medium text-gray-700 hover:text-emerald-600 transition-colors duration-200">
                        Login
                    </Link>
                    <button
                        type="button"
                        onClick={() => goTo('/signup')}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold shadow-sm hover:shadow-md transition-all duration-200"
                    >
                        Get Started
                    </button>
                </div>

                <button
                    type="button"
                    onClick={() => setOpen((v) => !v)}
                    aria-label={open ? 'Close menu' : 'Open menu'}
                    aria-expanded={open}
                    className="md:hidden flex flex-col items-center justify-center gap-1.5 h-10 w-10 relative"
                >
                    <span className={`block h-0.5 w-6 bg-gray-900 rounded-full transition-all duration-300 ${open ? 'rotate-45 translate-y-1' : ''}`} />
                    <span className={`block h-0.5 w-6 bg-gray-900 rounded-full transition-all duration-300 ${open ? '-rotate-45 -translate-y-0.5' : ''}`} />
                </button>
            </nav>

            {open && (
                <div className="md:hidden border-t border-gray-100 bg-white px-4 py-4 shadow-lg">
                    <div className="flex flex-col">
                        {NAV_ITEMS.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                end={item.to === '/'}
                                onClick={() => setOpen(false)}
                                className={({ isActive }) =>
                                    `py-2.5 text-sm font-medium rounded-lg px-3 transition-colors duration-200 ${
                                        isActive
                                            ? 'text-emerald-600 font-semibold bg-emerald-50'
                                            : 'text-gray-700 hover:text-emerald-600 hover:bg-gray-50'
                                    }`
                                }
                            >
                                {item.label}
                            </NavLink>
                        ))}
                    </div>
                    <div className="mt-3 pt-3 border-t border-gray-100 flex flex-col gap-2">
                        <Link
                            to="/login"
                            onClick={() => setOpen(false)}
                            className="py-2.5 text-sm font-medium text-center rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-50 transition-colors duration-200"
                        >
                            Login
                        </Link>
                        <button
                            type="button"
                            onClick={() => goTo('/signup')}
                            className="py-2.5 text-sm font-semibold text-center rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white transition-colors duration-200"
                        >
                            Get Started
                        </button>
                    </div>
                </div>
            )}
        </header>
    );
}

export default Navbar;