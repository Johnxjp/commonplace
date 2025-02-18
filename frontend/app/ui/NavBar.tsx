import Link from "next/link";

export default function NavBar({
	children,
}: Readonly<{ children: React.ReactNode }>) {
	return (
		<>
			<div className="relative flex-1 min-w-16 max-w-16 min-h-full bg-breakfast px-3">
				<div className="flex flex-col justify-center gap-y-3 pt-10">
					<button
						className="h-8 w-8 font-medium bg-white rounded-md hover:shadow-sm hover:border-md"
						title="home"
					>
						<Link
							className="flex items-center justify-center h-full w-full"
							href="/"
						>
							H
						</Link>
					</button>
					<button
						className="h-8 w-8 font-medium bg-white rounded-md hover:shadow-sm hover:border-md"
						title="library"
					>
						<Link
							className="flex items-center justify-center h-full w-full"
							href="/library"
						>
							L
						</Link>
					</button>

					<button
						className="h-8 w-8 font-medium bg-white rounded-md hover:shadow-sm hover:border-md"
						title="Conversation History"
					>
						<Link
							className="flex items-center justify-center h-full w-full"
							href="/conversation"
						>
							S
						</Link>
					</button>
					<button
						className="h-8 w-8 font-medium bg-white rounded-md hover:shadow-sm hover:border-md"
						title="Import"
					>
						<Link
							className="flex items-center justify-center h-full w-full"
							href="/import"
						>
							I
						</Link>
					</button>
				</div>
			</div>
			{children}
		</>
	);
}
