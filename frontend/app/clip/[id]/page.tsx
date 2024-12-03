// TODO: Load semantically similar and render

"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { dummyDocuments } from "@/placeholderData";
import BookDocument from "@/definitions";
import ImageThumbnail from "@/ui/ImageThumbnail";
import BookDocumentCard from "@/ui/BookDocumentCard";

export default function Document() {
	const [document, setDocument] = useState<BookDocument>();
	const [similarDocuments, setSimilarDocuments] = useState<BookDocument[]>([]);
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
			.then((data) => {
				console.log(data);
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

	// useEffect(() => {
	// 	// Get semantically similar documents
	// 	const serverUrl = "http://localhost:8000";
	// 	const resourceUrl = serverUrl + "/documents/" + params.id + "/similar";
	// 	const requestParams = {
	// 		method: "GET",
	// 		headers: {
	// 			Accept: "application/json",
	// 			"Content-Type": "application/json",
	// 		},
	// 	};

	// 	fetch(resourceUrl, requestParams)
	// 		.then((res) => res.json())
	// 		.then((data) => {
	// 			const similarDocuments: BookDocument[] = data.map((doc) => {
	// 				return {
	// 					id: doc.id,
	// 					title: doc.title,
	// 					authors: [doc.authors],
	// 					documentType: doc.document_type,
	// 					content: doc.content,
	// 					createdAt: new Date(doc.created_at),
	// 					updatedAt: doc.updated_at ? new Date(doc.updated_at) : null,
	// 					isClip: doc.is_clip,
	// 					clipStart: doc.clip_start,
	// 					clipEnd: doc.clip_end,
	// 					catalogueId: doc.catalogue_id,
	// 				};
	// 			});
	// 			setSimilarDocuments(similarDocuments);
	// 		})
	// 		.catch((err) => console.error(err));
	// }, [params.id]);

	function renderSimilarDocuments() {
		return (
			<>
				<hr className="border-1"></hr>
				<div
					className="flex w-full justify-left flex-col"
					id="semantically-similar"
				>
					<h2 className="text-lg font-bold mt-8">Similar Annotations</h2>
					<ul className="pt-8 pb-8 flex flex-col gap-4">
						{similarDocuments?.map((doc) => (
							<li key={doc.id}>
								<BookDocumentCard
									clampContent={false}
									document={doc}
									showTitle={true}
								/>
							</li>
						))}
					</ul>
				</div>
			</>
		);
	}

	return document === undefined ? (
		<></>
	) : (
		<div className="mx-auto flex flex-col items-center w-full h-full pl-8 pt-20 pr-14 max-w-3xl">
			<div className="flex flex-row gap-4 w-full">
				<ImageThumbnail
					width={20}
					height={20}
					src={"/vibrant.jpg"}
					alt={document.title}
				/>
				<div className="flex min-h-full flex-col w-full">
					<div>
						<h2 className="text-2xl font-bold line-clamp-1">
							{document.title}
						</h2>
						<p className="italic text-md">{document.authors.join(", ")}</p>
					</div>
				</div>
			</div>
			<div className="flex flex-col justify-left">
				<p className="w-full mt-6 italics text-xl">{document.content}</p>
				<p className="text-sm mt-4 italic text-slate-400">
					{`Location ${document.clipStart}`}
					{document.clipEnd ? `-${document.clipEnd}` : null}
				</p>
			</div>
			{similarDocuments.length > 0 && renderSimilarDocuments()}
		</div>
	);
}
