import Image from "next/image";
import React, { useState, useRef, useEffect, FormEvent } from "react";

// Types for the search state and results
// interface SearchState {
// 	query: string;
// 	tags: string[];
// }

interface SearchResult {
	id: string;
	title: string;
	description: string;
	// Add other result fields as needed
}

// interface SearchComponentProps {
// 	initialQuery?: string;
// 	initialTags?: string[];
// 	placeholder?: string;
// }

export default function HomeSearchBar() {
	const maxHeight = 200;
	const [searchValue, setSearchValue] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [results, setResults] = useState<SearchResult[] | null>(null);
	const textareaRef = useRef<HTMLTextAreaElement>(null);

	// Auto-resize function
	function adjustTextareaHeight() {
		const textarea = textareaRef.current;
		if (textarea) {
			// Reset height to get the correct scrollHeight
			textarea.style.height = "auto";

			// Calculate new height
			const newHeight = Math.min(textarea.scrollHeight, maxHeight);
			textarea.style.height = `${newHeight}px`;
		}
	}

	useEffect(() => {
		adjustTextareaHeight();
	}, [searchValue, maxHeight]);

	const handleSubmit = async (e: FormEvent) => {
		e.preventDefault();
		setIsLoading(true);
		setError(null);

		try {
			const response = await fetch("/api/search", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(searchValue),
			});

			if (!response.ok) {
				throw new Error("Search request failed");
			}

			const data = await response.json();
			setResults(data);
		} catch (error) {
			setError(error instanceof Error ? error.message : "An error occurred");
			setResults(null);
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="w-full max-w-4xl mx-auto px-1 md:px-2">
			<form onSubmit={handleSubmit} className="mb-8">
				<div className="flex gap-1 border rounded-lg py-1 px-1">
					<textarea
						ref={textareaRef}
						value={searchValue}
						onChange={(e) => setSearchValue(e.target.value)}
						placeholder="Explore your books..."
						className="w-full px-4 py-2 pr-10 rounded-lg outline-none resize-none overflow-y-auto min-h-20"
						disabled={isLoading}
						style={{
							overflowY:
								textareaRef?.current?.scrollHeight > maxHeight
									? "auto"
									: "hidden",
							height: 10,
						}}
						onKeyDown={(e) => {
							if (e.key === "Enter" && !e.shiftKey) {
								e.preventDefault();
								handleSubmit(e);
							}
						}}
					/>
					<button
						type="submit"
						disabled={isLoading || !searchValue.trim()}
						className="max-h-8 w-8 text-white bg-slate-100 flex items-center justify-center rounded-xl hover:bg-slate-300 disabled:cursor-not-allowed"
					>
						<Image
							src="/send_message.png"
							width={16}
							height={16}
							alt="Search"
						/>
					</button>
				</div>
			</form>

			{/* Results section */}
			{error && (
				<div className="text-red-600 mb-4 p-4 bg-red-50 rounded-lg">
					{error}
				</div>
			)}

			{results && (
				<div className="space-y-6">
					{results.length === 0 ? (
						<p className="text-gray-600 text-center py-8">
							No results found for "{searchValue}"
						</p>
					) : (
						results.map((result) => (
							<div
								key={result.id}
								className="p-4 border rounded-lg hover:shadow-md transition-shadow"
							>
								<h3 className="text-lg font-semibold mb-2">{result.title}</h3>
								<p className="text-gray-600">{result.description}</p>
							</div>
						))
					)}
				</div>
			)}
		</div>
	);
}
