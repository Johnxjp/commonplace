"use client";

import { useState, useEffect } from "react";

import { getTimeOfDay } from "@/utils";
import BookDocument from "@/definitions";
import BookDocumentCard from "@/ui/BookDocumentCard";
import HomeSearchBar from "@/HomeSearchBar";
import { dummyDocuments } from "@/placeholderData";

function BookDocumentSampleGrid({ documents }: { documents: BookDocument[] }) {
	return (
		<div className="mx-auto max-w-4xl w-full px-1 md:px-2 flex">
			<ul className="grid w-full md:grid-cols-3 gap-3">
				{documents.map((doc) => (
					<li className="flex-1" key={doc.id}>
						<BookDocumentCard
							document={doc}
							clampContent={true}
							showTitle={true}
							showAuthors={false}
							showMetadata={false}
						/>
					</li>
				))}
			</ul>
		</div>
	);
}

export default function Home() {
	const timeOfDay: string = getTimeOfDay();
	const [documents, setDocuments] = useState<BookDocument[]>([]);

	useEffect(() => {
		setDocuments(dummyDocuments);
		// const serverUrl = "http://localhost:8000";
		// const resourceUrl = serverUrl + "/documents?limit=6&random=true";
		// const requestParams = {
		// 	method: "GET",
		// 	headers: {
		// 		Accept: "application/json",
		// 		"Content-Type": "application/json",
		// 	},
		// };

		// fetch(resourceUrl, requestParams)
		// 	.then((res) => res.json())
		// 	.then((data) => {
		// 		console.log(data);
		// 		const documents: BookDocument[] = data.map((doc) => {
		// 			return {
		// 				id: doc.id,
		// 				title: doc.title,
		// 				authors: [doc.authors],
		// 				documentType: doc.document_type,
		// 				content: doc.content,
		// 				createdAt: new Date(doc.created_at),
		// 				updatedAt: doc.updated_at ? new Date(doc.updated_at) : null,
		// 				isClip: doc.is_clip,
		// 				clipStart: doc.clip_start,
		// 				clipEnd: doc.clip_end,
		// 				catalogueId: doc.catalogue_id,
		// 			};
		// 		});
		// 		setDocuments(documents);
		// 		console.log(documents);
		// 	})
		// 	.catch((err) => console.error(err));
	}, []);

	return (
		<div className="min-h-full w-full min-w-0 flex-1">
			<main className="mx-auto mt-4 h-full w-full max-w-7xl flex md:pl-8 !mt-0 flex flex-col items-center gap-8 pt-12 pr-14">
				<h1 className="">
					Good {timeOfDay.charAt(0).toUpperCase() + timeOfDay.slice(1)}
				</h1>
				<h2 className="text-2xl">Just Wander</h2>
				<BookDocumentSampleGrid documents={documents} />
				<HomeSearchBar />
			</main>
		</div>
	);
}
