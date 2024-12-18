// app/import/FileUploader.tsx
import { useState } from "react";

export function ReadwiseUploader() {
	const [file, setFile] = useState<File | null>(null);
	const [isUploading, setIsUploading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [uploadSuccess, setUploadSuccess] = useState<boolean | null>(null);

	const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const selectedFile = event.target.files?.[0];
		if (selectedFile) {
			if (selectedFile.name.endsWith(".csv")) {
				setFile(selectedFile);
				setError(null);
			} else {
				setError("Please select a valid Readwise file (.csv)");
				setFile(null);
			}
			setUploadSuccess(null);
		}
	};

	const handleUpload = async () => {
		if (!file) return;

		setIsUploading(true);
		setError(null);
		setUploadSuccess(null);

		try {
			const formData = new FormData();
			formData.append("csv_file", file);

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
			setUploadSuccess(true);
		} catch (err) {
			setUploadSuccess(false);
			setError(err instanceof Error ? err.message : "An error occurred");
		} finally {
			setIsUploading(false);
		}
	};

	return (
		<div className="space-y-6">
			<div>
				<h2 className="text-xl font-semibold mb-2">Readwise</h2>
				<p className="text-gray-600">Import annotations from Readwise.</p>
			</div>

			<div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
				<input
					type="file"
					accept=".csv,.txt"
					onChange={handleFileChange}
					className="hidden"
					id="kindle-file"
				/>
				<label
					htmlFor="kindle-file"
					className="cursor-pointer text-blue-500 hover:text-blue-600"
				>
					Click to select file
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
			{/* Show success message same style as button but green for success and red for fail */}
			{uploadSuccess === true && (
				<p className="w-full py-2 px-4 rounded-lg text-center bg-green-500 text-white">
					Upload successful
				</p>
			)}
			{uploadSuccess === false && (
				<p className="w-full py-2 px-4 rounded-lg text-center bg-red-500 text-white">
					Upload failed
				</p>
			)}
		</div>
	);
}
