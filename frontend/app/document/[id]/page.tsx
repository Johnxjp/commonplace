// Document is a container for multiple annotations
// It may also contain full text of the document
"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import BookDocument from "@/definitions";
import ImageThumbnail from "@/ui/ImageThumbnail";
import BookDocumentCard from "@/ui/BookDocumentCard";

type containerDocument = {
	id: string;
	title: string;
	authors: string[];
	thumbnail_path: string;
};

export default function DocumentContainer() {
	const [containerDocument, setContainerDocument] =
		useState<containerDocument>();
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

	return (
		containerDocument && (
			<div className="mx-auto flex flex-col items-center w-full h-full pl-8 pt-20 pr-14 max-w-3xl">
				<div className="flex flex-row gap-4 w-full">
					{ImageThumbnail(20, 20, "/vibrant.jpg", containerDocument.title)}
					<div className="flex min-h-full flex-col w-full">
						<div>
							<h2 className="text-2xl font-bold line-clamp-1">
								{containerDocument.title}
							</h2>
							<p className="italic text-md">
								{containerDocument.authors.join(", ")}
							</p>
							<p>{`${annotations.length} Highlight` + `${annotations.length > 1 ? 's' : ''}`}</p>
						</div>
					</div>
				</div>
				<div className="flex w-full justify-left flex-col">
					<ul className="pt-8 pb-8 flex flex-col gap-4">
						{annotations?.map((doc) => (
							<li key={doc.id}>
								<BookDocumentCard clampContent={false} document={doc} />
							</li>
						))}
					</ul>
				</div>
			</div>
		)
	);
}
