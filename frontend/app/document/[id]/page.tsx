// Document is a container for multiple annotations
// It may also contain full text of the document
"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Clip, Book } from "@/definitions";
import ImageThumbnail from "@/ui/ImageThumbnail";
import BookClipCard from "@/ui/BookClipCard";

type FetchApiResponse = {
	annotations: {
		id: string;
		content: string;
		created_at: Date;
		updated_at: Date | null;
		clip_start: number;
		clip_end: number | null;
		document_id: string;
		location_type: string;
	}[];
	total: number;
	source: {
		id: string;
		title: string;
		authors: string;
		user_thumbnail_path: string | null;
		created_at: Date;
		updated_at: Date | null;
		catalogue_id: string | null;
	};
};

export default function DocumentContainer() {
	const [book, setBook] = useState<Book>();
	const [clips, setClips] = useState<Clip[]>([]);
	const params = useParams();

	// use effect to fetch document data
	useEffect(() => {
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/document/" + params.id + "/annotations";
		const requestParams = {
			method: "GET",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};

		fetch(resourceUrl, requestParams)
			.then((res) => res.json())
			.then((data: FetchApiResponse) => {
				const authors = data.source.authors
					? data.source.authors.split(";")
					: [];
				const book: Book = {
					id: data.source.id,
					title: data.source.title,
					authors: authors,
					thumbnailUrl: data.source.user_thumbnail_path,
					catalogueId: data.source.catalogue_id,
					createdAt: new Date(data.source.created_at),
					updatedAt: data.source.updated_at
						? new Date(data.source.updated_at)
						: null,
				};
				setBook(book);
				const clips: Clip[] = data.annotations.map((annotation) => {
					return {
						id: annotation.id,
						book: book,
						content: annotation.content,
						createdAt: new Date(annotation.created_at),
						updatedAt: annotation.updated_at
							? new Date(annotation.updated_at)
							: null,
						clipStart: annotation.clip_start,
						clipEnd: annotation.clip_end,
						locationType: annotation.location_type,
					};
				});
				setClips(clips);
			})
			.catch((err) => console.error(err));
	}, [params.id]);

	return (
		book && (
			<div className="mx-auto flex flex-col items-center w-full h-full pl-8 pt-20 pr-14 max-w-3xl">
				<div className="flex flex-row gap-4 w-full">
					<ImageThumbnail
						width={100}
						height={100}
						src={"/vibrant.jpg"}
						alt={book.title}
					/>
					<div className="flex min-h-full flex-col w-full">
						<div>
							<h2 className="text-2xl font-bold line-clamp-1">{book.title}</h2>
							<p className="italic text-md">{book.authors.join(", ")}</p>
							<p>
								{`${clips.length} Highlight` + `${clips.length > 1 ? "s" : ""}`}
							</p>
						</div>
					</div>
				</div>
				<div className="flex w-full justify-left flex-col">
					<ul className="pt-8 pb-8 flex flex-col gap-4">
						{clips?.map((doc) => (
							<li key={doc.id}>
								<BookClipCard
									clampContent={false}
									clip={doc}
									showMetadata={true}
									showDeleteButton={true}
								/>
							</li>
						))}
					</ul>
				</div>
			</div>
		)
	);
}
