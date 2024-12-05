"use client";

import { useEffect, useState } from "react";

import { ConversationMetadata } from "@/definitions";

type GetConversationMetadataResponse = {
	id: string;
	name: string;
	created_at: string;
	updated_at: string;
	current_leaf_message_id: string | null;
	model: string | null;
	summary: string | null;
	message_count: number;
};

export default function ConversationHistory() {
	const [conversations, setConversations] = useState<ConversationMetadata[]>(
		[]
	);

	// Hits backend for conversation history
	useEffect(() => {
		const serverUrl = "http://localhost:8000";
		const resourceUrl =
			serverUrl + "/conversation?sort=updated_at&order_by=desc";
		const requestParams = {
			method: "GET",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};

		fetch(resourceUrl, requestParams)
			.then((res) => res.json())
			.then((data: GetConversationMetadataResponse[]) => {
				const conversationMetadata: ConversationMetadata[] = data.map(
					(conversation) => {
						return {
							id: conversation.id,
							name: conversation.name,
							createdAt: new Date(conversation.created_at),
							updatedAt: new Date(conversation.updated_at),
							currentLeafMessageId: conversation.current_leaf_message_id,
							model: conversation.model,
							summary: conversation.summary,
							messageCount: conversation.message_count,
						};
					}
				);
				setConversations(conversationMetadata);
			})
			.catch((error) => {
				console.error("Error:", error);
			});
	}, []);
	return (
		<div className="mx-auto mt-4 w-full max-w-7xl flex-1 px-4 pb-20 md:pl-8 lg:mt-6 md:pr-14">
			<ul className="flex flex-col gap-3"></ul>
			{conversations.map((conversation) => (
				<li
					className="w-full border border-border-300 hover:border-border-200 group relative flex cursor-pointer flex-col gap-1.5 rounded-xl py-5 px-6 transition-all ease-in-out hover:shadow-sm active:scale-[0.98] md:gap-4"
					key={conversation.id}
				>
					<div className="flex items-center gap-2">
						<div className="flex flex-col">
							<div className="font-bold line-clamp-1">{conversation.name}</div>
							<div className="flex items-center gap-2">
								<div className="text-sm text-gray-500">
									{conversation.updatedAt.toLocaleDateString()}
								</div>
								<div className="text-sm text-gray-500">
									{conversation.messageCount} messages
								</div>
							</div>
						</div>
					</div>
				</li>
			))}
		</div>
	);
}
