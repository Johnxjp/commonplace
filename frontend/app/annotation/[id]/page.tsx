// TODO: Load semantically similar and render

"use client";

import BookDocument from "@/definitions";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

export default function Document() {
	const [document, setDocument] = useState<BookDocument | null>(null);
	const params = useParams();

	// use effect to fetch document data
	useEffect(() => {
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/documents/" + params.id;
		const requestParams = {
			method: "GET",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};

		fetch(resourceUrl, requestParams)
			.then((res) => res.json())
			.then((data) => {
				const document: BookDocument = {
					id: data.id,
					title: data.title,
					authors: [data.authors],
					documentType: data.document_type,
					content: data.content,
					createdAt: new Date(data.created_at),
					updatedAt: data.updated_at ? new Date(data.updated_at) : null,
					isClip: data.is_clip,
					clipStart: data.clip_start,
					clipEnd: data.clip_end,
					catalogueId: data.catalogue_id,
				};
				setDocument(document);
			})
			.catch((err) => console.error(err));
	}, [params.id]);

	return document === null ? (
		<></>
	) : (
		<div className="flex flex-col items-center">
			<h1>{document.title}</h1>
			<h2>{document.authors.join(", ")}</h2>
			<p>{document.content}</p>
		</div>
	);
}
