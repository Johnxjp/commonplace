// Document is a container for multiple annotations
// It may also contain full text of the document
"use client";

import BookDocument from "@/definitions";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

type containerDocument = {
	id: string;
	title: string;
	authors: string[];
	thumbnail_path: string;
};

export default function DocumentContainer() {
	const [containerDocument, setContainerDocument] =
		useState<containerDocument | null>(null);
	const [annotations, setAnnotations] = useState<BookDocument[]>([]);
	const params = useParams();

	// use effect to fetch document data
	useEffect(() => {
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/documents/" + params.id + "/annotations";
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
				const authors = data.authors ? data.authors.split(";") : [];
				const document = {
					id: data.id,
					title: data.title,
					authors: authors,
					thumbnail_path: data.thumbnail_path,
				};
				setContainerDocument(document);
				console.log(data);
				const annotations = data["annotations"].map((annotation) => {
					const authors = annotation.authors
						? annotation.authors.split(";")
						: [];
					return {
						id: annotation.id,
						title: annotation.title,
						authors: authors,
						documentType: annotation.document_type,
						content: annotation.content,
						createdAt: new Date(annotation.created_at),
						updatedAt: annotation.updated_at
							? new Date(annotation.updated_at)
							: null,
						isClip: annotation.is_clip,
						clipStart: annotation.clip_start,
						clipEnd: annotation.clip_end,
						catalogueId: annotation.catalogue_id,
					};
				});
				setAnnotations(annotations);
			})
			.catch((err) => console.error(err));
	}, [params.id]);

	return containerDocument === null ? (
		<></>
	) : (
		<div className="flex flex-col items-center">
			<h1>{containerDocument.title}</h1>
			<h2>{containerDocument.authors.join(", ")}</h2>
			<div>
				<ul className="gap-y-2">
					{annotations.map((annotation) => (
						<li key={annotation.id}>
							{/* <h3>{annotation.title}</h3> */}
							<p>{annotation.content}</p>
						</li>
					))}
				</ul>
			</div>
		</div>
	);
}
