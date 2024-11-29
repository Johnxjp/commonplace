export default function NavBar({
	children,
}: Readonly<{ children: React.ReactNode }>) {
	return (
		<>
			<div className="flex-1 w-16 max-w-16 h-full bg-orange-100 px-3">
				<div className="flex flex-col justify-center gap-y-3 pt-10">
					<button
						className="h-8 w-8 font-medium bg-white flex items-center justify-center rounded-md hover:shadow-sm hover:border-md"
						title="home"
					>
						H
					</button>
					<button
						className="h-8 w-8 font-medium bg-white flex items-center justify-center rounded-md hover:shadow-sm hover:border-md"
						title="library"
					>
						L
					</button>

					<button
						className="h-8 w-8 font-medium bg-white flex items-center justify-center rounded-md hover:shadow-sm hover:border-md"
						title="search_history"
					>
						S
					</button>
				</div>
			</div>
			{children}
		</>
	);
}
