"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useConversationStore } from "@/store/useConversationStore";
import { Message, Clip, ConversationMetadata } from "@/definitions";

export default function Conversation() {
	// This page displays the conversation between the user and the system.
	// The url is defined by the id of the conversation.
	const params = useParams();
	const conversationId = params.id;
	const [conversationMetadata, setConversationMetadata] =
		useState<ConversationMetadata | null>(null);
	const { query, clearConversation } = useConversationStore();

	// Messages need content, role, something for ordering e.g. parent_message_id.
	// Created at works in beginning but not if can retry.
	const [messages, setMessages] = useState<Message[]>([]);
	const [loading, setLoading] = useState(false);

	// TODO: We want this to only initialise a conversation when
	// a query is sumbitted. A user should be able to return to this
	// page and view the conversation without a request being made.
	useEffect(() => {
		// const document = dummyDocuments.find((doc) => doc.id === params.id);
		// setDocument(document);

		if (!conversationId) return;
		if (query) {
			setLoading(true);
			const asyncFunction = async () => {
				const message: Message = await addUserMessage(query, "user", null);
				setMessages((prevMessages) => [...prevMessages, message]);

				const response: Message = await generateAnswer(
					query,
					message.parent_message_id
				);
				setMessages((prevMessages) => [...prevMessages, response]);
				setLoading(false);
			};
			asyncFunction().catch((error) => {
				console.log("Throwing error when generating answer");
				console.error(error);
				setLoading(false);
			});
			// Clear the store after generating the answer
			clearConversation();
		} else if (!loading && messages.length === 0) {
			const asyncFunction = async () => {
				setLoading(true);
				const convo = await fetchConversation();
				setMessages(convo.message);
				setConversationMetadata(convo.metadata);
				setLoading(false);
			};
			asyncFunction().catch((error) => {
				console.error(error);
				setLoading(false);
			});
		}
	}, [conversationId, query]);

	async function addUserMessage(
		query: string,
		sender: string = "user",
		parent_message_id: string | null = null
	): Promise<Message> {
		try {
			const message = {
				content: query,
				sender: sender,
				parent_message_id: parent_message_id,
			};
			console.log("Adding user message:", message);
			const response = await fetch(
				"http://localhost:8000/conversation/" + conversationId + "/message",
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(message),
				}
			);
			if (!response.ok) {
				throw new Error("Failed to add user message");
			}

			const data = await response.json();
			const newMessage = {
				id: data.id,
				content: data.content,
				sender: data.sender,
				parent_message_id: data.parent_id,
				createdAt: new Date(data.created_at),
				updatedAt: new Date(data.updated_at),
				contentSources: [],
			};
			return newMessage;
		} catch (error) {
			console.error(error);
			throw new Error("Failed to add user message");
		}
	}

	async function fetchConversation() {
		// Fetch conversation by id
		// Set messages
		const response = await fetch(
			"http://localhost:8000/conversation/" + conversationId,
			{
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
			}
		);
		const data = await response.json();
		const conversationMetadata: ConversationMetadata = {
			id: data.id,
			name: data.name,
			createdAt: new Date(data.created_at),
			updatedAt: new Date(data.updated_at),
			currentLeafMessageId: data.current_leaf_message_id,
			model: data.model,
			summary: data.summary,
			messageCount: data.message_count,
		};
		const messages = data.messages;
		return { message: messages, metadata: conversationMetadata };
	}

	async function generateAnswer(
		query: string,
		parent_message_id: string | null
	) {
		try {
			const serverUrl = "http://localhost:8000";
			const resourceUrl = `${serverUrl}/conversation/${conversationId}/completion`;
			const params = {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					query: query,
					parent_message_id: parent_message_id,
				}),
			};
			const response = await fetch(resourceUrl, params);
			const data = await response.json();
			const contentSources: Clip[] = data.sources.map((source) => {
				return {
					id: source.id,
					book: {
						id: source.document_id,
						title: source.title,
						authors: source.authors,
						createdAt: new Date(source.created_at),
						updatedAt: source.updated_at ? new Date(source.updated_at) : null,
						catalogueId: source.catalogue_id,
						thumbnailUrl: source.user_thumbnail_path,
					},
					content: source.content,
					createdAt: new Date(source.created_at),
					updatedAt: source.updated_at ? new Date(source.updated_at) : null,
					locationType: source.location_type,
					clipStart: source.clip_start,
					clipEnd: source.clip_end,
				};
			});
			const responseMessage = {
				id: data.id,
				content: data.content,
				sender: data.sender,
				parent_message_id: data.parent_id,
				createdAt: new Date(data.created_at),
				updatedAt: new Date(data.updated_at),
				contentSources: contentSources,
			};
			return responseMessage;
		} catch (error) {
			console.error("Failed to generate response:", error);
			throw error;
		}
	}

	function renderConversationName() {
		const name =
			conversationMetadata === null || conversationMetadata.name === null
				? "Untitled"
				: conversationMetadata.name;

		return <h1 className="text-lg font-bold p-2 pb-8">{name}</h1>;
	}

	function renderMessage(message: Message, color: string) {
		console.log(message);
		return (
			<div
				className={"rounded-2xl border border-solid py-3.5 px-4" + color}
				key={message.id}
			>
				<h2 className="text-sm italic">{message.sender}</h2>
				<p>{message.content}</p>
			</div>
		);
	}

	return (
		<div className="mx-auto mt-4 w-full max-w-7xl flex-1 px-4 pb-20 md:pl-8 lg:mt-6 md:pr-14">
			{renderConversationName()}
			<div className="flex flex-col gap-y-4">
				{messages.map((message) => {
					const color =
						message.sender === "user" ? " bg-orange-100" : " bg-white";
					return renderMessage(message, color);
				})}
			</div>
			<div>
				{loading && (
					<div className="flex justify-center items-center">
						<p>Loading...</p>
					</div>
				)}
			</div>
		</div>
	);
}
