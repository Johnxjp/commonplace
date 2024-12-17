// TODO: Load semantically similar and render

"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Clip, Book } from "@/definitions";
import ImageThumbnail from "@/ui/ImageThumbnail";
import BookDocumentCard from "@/ui/BookClipCard";

type FetchClipApiResponse = {
	id: string;
	title: string;
	authors: string | null;
	document_id: string;
	created_at: Date;
	updated_at: Date | null;
	content: string;
	location_type: string;
	clip_start: number;
	clip_end: number | null;
	catalogue_id: string;
	thumbnail_path: string;
};

export default function Document() {
	const [clip, setClip] = useState<Clip>();
	const [similarClips, setSimilarClips] = useState<Clip[]>([]);
	const params = useParams();

	// use effect to fetch document data
	useEffect(() => {
		// const document = dummyDocuments.find((doc) => doc.id === params.id);
		// setDocument(document);
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/clip/" + params.id;
		const requestParams = {
			method: "GET",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};

		fetch(resourceUrl, requestParams)
			.then((res) => res.json())
			.then((data: FetchClipApiResponse) => {
				const book: Book = {
					id: data.document_id,
					title: data.title,
					authors: data.authors ? data.authors.split(";") : [],
					createdAt: new Date(data.created_at), // Wrong for now
					updatedAt: data.updated_at ? new Date(data.updated_at) : null,
					catalogueId: data.catalogue_id,
					thumbnailUrl: data.thumbnail_path,
				};
				const clip: Clip = {
					id: data.id,
					book: book,
					content: data.content,
					createdAt: new Date(data.created_at),
					updatedAt: data.updated_at ? new Date(data.updated_at) : null,
					locationType: data.location_type,
					clipStart: data.clip_start,
					clipEnd: data.clip_end,
				};
				setClip(clip);
			})
			.catch((err) => console.error(err));
	}, [params.id]);

	useEffect(() => {
		// Get semantically similar documents
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/clip/" + params.id + "/similar";
		const requestParams = {
			method: "GET",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};

		fetch(resourceUrl, requestParams)
			.then((res) => res.json())
			.then((data: FetchClipApiResponse[]) => {
				const similarClips: Clip[] = data.map((doc) => {
					const book: Book = {
						id: doc.document_id,
						title: doc.title,
						authors: doc.authors ? doc.authors.split(";") : [],
						createdAt: new Date(doc.created_at),
						updatedAt: doc.updated_at ? new Date(doc.updated_at) : null,
						catalogueId: doc.catalogue_id,
						thumbnailUrl: doc.thumbnail_path,
					};

					return {
						id: doc.id,
						book: book,
						content: doc.content,
						createdAt: new Date(doc.created_at),
						updatedAt: doc.updated_at ? new Date(doc.updated_at) : null,
						locationType: doc.location_type,
						clipStart: doc.clip_start,
						clipEnd: doc.clip_end,
					};
				});
				setSimilarClips(similarClips);
			})
			.catch((err) => console.error(err));
	}, [params.id]);

	function rendersimilarClips() {
		return (
			<>
				<hr className="border-1"></hr>
				<div
					className="flex w-full justify-left flex-col"
					id="semantically-similar"
				>
					<h2 className="text-lg font-bold mt-8">Similar Annotations</h2>
					<ul className="pt-8 pb-8 flex flex-col gap-4">
						{similarClips?.map((doc) => (
							<li key={doc.id}>
								<BookDocumentCard
									clampContent={false}
									clip={doc}
									showTitle={true}
								/>
							</li>
						))}
					</ul>
				</div>
			</>
		);
	}

	return clip === undefined ? (
		<></>
	) : (
		<div className="mx-auto flex flex-col items-center w-full h-full pl-8 pt-20 pr-14 max-w-3xl">
			<Link className="w-full" href={`/document/${clip.book.id}`}>
				<div className="flex flex-row gap-4 w-full">
					<ImageThumbnail
						width={100}
						height={100}
						src={"/vibrant.jpg"}
						alt={clip.book.title}
					/>
					<div className="flex min-h-full flex-col w-full">
						<div>
							<h2 className="text-2xl font-bold line-clamp-1">
								{clip.book.title}
							</h2>
							<p className="italic text-md">{clip.book.authors.join(", ")}</p>
						</div>
					</div>
				</div>
			</Link>
			<div className="flex flex-col justify-left">
				<p className="w-full mt-6 italics text-xl">{clip.content}</p>
				<p className="text-sm mt-4 italic text-slate-400">
					{`Location ${clip.clipStart}`}
					{clip.clipEnd ? `-${clip.clipEnd}` : null}
				</p>
			</div>
			{similarClips.length > 0 && rendersimilarClips()}
		</div>
	);
}
