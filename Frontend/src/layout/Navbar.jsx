

export const Navbar = () => {
  return (
    <header className=" ">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">DATA X</h1>
          <nav>
            <ul className="flex space-x-4">
              <li><a href="/" className="text-black hover:text-blue-500">Home</a></li>
              <li><a href="/features" className="text-black hover:text-blue-500">Features</a></li>
              <li><a href="/pricing" className="text-black hover:text-blue-500">Pricing</a></li>
              <li><a href="/contact" className="text-black hover:text-blue-500">Contact</a></li>
            </ul>
          </nav>
        </div>
      </header>
  )
}
