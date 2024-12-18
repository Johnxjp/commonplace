// app/import/page.tsx
"use client";

import { useState } from "react";
import { FileUploader } from "@/import/FileUploader";
import { ReadwiseUploader } from "@/import/ReadwiseUploader";

export default function ImportPage() {
	const [importMethod, setImportMethod] = useState<
		"readwise" | "kindle" | null
	>(null);

	return (
		<div className="min-h-screen w-full">
			<main className="max-w-4xl mx-auto p-6">
				<div className="rounded-lg p-8">
					<h1 className="text-2xl font-bold text-gray-900 mb-6">
						Import Your Knowledge
					</h1>

					{!importMethod ? (
						<div className="space-y-4">
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
								<button
									onClick={() => setImportMethod("readwise")}
									className="flex items-center justify-center gap-2 p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
								>
									{/* <img
										src="/readwise-icon.svg"
										alt="Readwise"
										className="w-8 h-8"
									/> */}
									<span className="text-lg font-medium">
										Import from Readwise
									</span>
								</button>
								<button
									onClick={() => setImportMethod("kindle")}
									className="flex items-center justify-center gap-2 p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
								>
									{/* <img
										src="/kindle-icon.svg"
										alt="Kindle"
										className="w-8 h-8"
									/> */}
									<span className="text-lg font-medium">
										Import from Kindle File
									</span>
								</button>
							</div>
						</div>
					) : (
						<div>
							<button
								onClick={() => setImportMethod(null)}
								className="mb-6 text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
							>
								<span>←</span> Back to import options
							</button>

							{importMethod === "readwise" ? (
								<ReadwiseUploader />
							) : (
								<FileUploader />
							)}
						</div>
					)}
				</div>
			</main>
		</div>
	);
}
