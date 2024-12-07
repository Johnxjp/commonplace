import Image from "next/image";
import { useRouter } from "next/navigation";
import React, { useState, useRef, useEffect, FormEvent } from "react";
import { useConversationStore } from "@/store/useConversationStore";

// Types for the search state and results
// interface SearchState {
// 	query: string;
// 	tags: string[];
// }

// interface SearchResult {
// 	id: string;
// 	title: string;
// 	description: string;
// 	// Add other result fields as needed
// }

// interface SearchComponentProps {
// 	initialQuery?: string;
// 	initialTags?: string[];
// 	placeholder?: string;
// }

export default function HomeSearchBar() {
	const maxHeight = 200;
	const [searchValue, setSearchValue] = useState("");
	const [loading, setLoading] = useState(false);
	const textareaRef = useRef<HTMLTextAreaElement>(null);
	const router = useRouter();
	const setConversation = useConversationStore(
		(state) => state.setConversation
	);

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

	async function handleSubmit(e: FormEvent) {
		e.preventDefault();
		setLoading(true);

		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/conversation";
		const requestParams = {
			method: "POST",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
			body: null,
		};

		try {
			const query = searchValue;
			const response = await fetch(resourceUrl, requestParams);
			console.log("Response:", response);
			const data = await response.json();
			console.log("Data:", data);
			// Set the conversation in Zustand store
			if (data.id === undefined || data.id === null){
				throw new Error("Conversation ID not found in response");
			}
			setConversation(query, data.id);
			console.log(useConversationStore.getState());
			console.log(
				`"Conversation successfully created. Navigating to conversation/${data.id}"`
			);
			router.push(`/conversation/${data.id}`);

			// setResults(data);
		} catch (error) {
			console.error("Error:", error);
		} finally {
			setLoading(false);
		}
	}

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
						disabled={loading}
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
						disabled={loading || !searchValue.trim()}
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
		</div>
	);
}
