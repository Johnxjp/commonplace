import "./globals.css";
import NavBar from "@/ui/NavBar";

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en">
			<body>
				<div className="min-h-screen w-screen flex flex-row">
					<NavBar>{children}</NavBar>
				</div>
			</body>
		</html>
	);
}
