// app/import/FileUploader.tsx
import { useState } from "react";

export function FileUploader() {
	const [file, setFile] = useState<File | null>(null);
	const [isUploading, setIsUploading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const selectedFile = event.target.files?.[0];
		if (selectedFile) {
			if (selectedFile.name.endsWith(".txt")) {
				setFile(selectedFile);
				setError(null);
			} else {
				setError("Please select a valid Kindle export file (.txt)");
				setFile(null);
			}
		}
	};

	const handleUpload = async () => {
		if (!file) return;

		setIsUploading(true);
		setError(null);

		try {
			const formData = new FormData();
			formData.append("file", file);

			const serverUrl = "http://localhost:8000";
			const resourceUrl = serverUrl + "/document/upload/readwise";
			const response = await fetch(resourceUrl, {
				method: "POST",
				body: formData,
			});

			if (!response.ok) {
				throw new Error("Failed to upload file");
			}

			// Handle successful upload
			// You might want to redirect or show a success message
		} catch (err) {
			setError(err instanceof Error ? err.message : "An error occurred");
		} finally {
			setIsUploading(false);
		}
	};

	return (
		<div className="space-y-6">
			<div>
				<h2 className="text-xl font-semibold mb-2">Import Kindle Highlights</h2>
				<p className="text-gray-600">
					Upload your Kindle highlights export file to import your annotations.
				</p>
			</div>

			<div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
				<input
					type="file"
					accept=".txt"
					onChange={handleFileChange}
					className="hidden"
					id="kindle-file"
				/>
				<label
					htmlFor="kindle-file"
					className="cursor-pointer text-blue-500 hover:text-blue-600"
				>
					Click to select your Kindle export file
				</label>
				{file && (
					<p className="mt-2 text-sm text-gray-600">
						Selected file: {file.name}
					</p>
				)}
			</div>

			{error && <p className="text-red-500 text-sm">{error}</p>}

			<button
				onClick={handleUpload}
				disabled={!file || isUploading}
				className="w-full py-2 px-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
			>
				{isUploading ? "Uploading..." : "Upload and Import"}
			</button>
		</div>
	);
}
