"use client";

import { useState, useEffect } from "react";

import { getTimeOfDay } from "@/utils";
import { Clip, Book } from "@/definitions";
import BookDocumentCard from "@/ui/BookClipCard";
import HomeSearchBar from "@/HomeSearchBar";
// import { dummyDocuments } from "@/placeholderData";

function ClipSampleGrid({ clips }: { clips: Clip[] }) {
	return (
		<div className="mx-auto max-w-4xl w-full px-1 md:px-2 flex">
			<ul className="grid w-full md:grid-cols-3 gap-3">
				{clips.map((clip) => (
					<li className="flex-1" key={clip.id}>
						<BookDocumentCard
							clip={clip}
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

type FetchClipsApiResponse = {
	id: string;
	title: string;
	authors: string;
	content: string;
	document_id: string;
	created_at: string;
	location_type: string;
	updated_at: string | null;
	clip_start: number | null;
	clip_end: number | null;
	catalogue_id: string;
	thumbnail_url: string | null;
}[];

export default function Home() {
	const timeOfDay: string = getTimeOfDay();
	const [clips, setClips] = useState<Clip[]>([]);

	useEffect(() => {
		// setClips(dummyDocuments);
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/clip?limit=6&random=true";
		const requestParams = {
			method: "GET",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};

		fetch(resourceUrl, requestParams)
			.then((res) => res.json())
			.then((data: FetchClipsApiResponse) => {
				const clips: Clip[] = data.map((response) => {
					const book: Book = {
						id: response.document_id,
						title: response.title,
						authors:
							response.authors !== null ? response.authors.split(";") : [],
						createdAt: new Date(response.created_at),
						updatedAt: response.updated_at
							? new Date(response.updated_at)
							: null,
						catalogueId: response.catalogue_id,
						thumbnailUrl: response.thumbnail_url,
					};

					return {
						id: response.id,
						book: book,
						content: response.content,
						createdAt: new Date(response.created_at),
						updatedAt: response.updated_at
							? new Date(response.updated_at)
							: null,
						locationType: response.location_type,
						clipStart: response.clip_start,
						clipEnd: response.clip_end,
					};
				});
				setClips(clips);
			})
			.catch((err) => console.error(err));
	}, []);

	return (
		<div className="min-h-full w-full min-w-0 flex-1">
			<main className="mx-auto mt-4 h-full w-full max-w-7xl flex md:pl-8 !mt-0 flex flex-col items-center gap-8 pt-12 pr-14">
				<h1 className="">
					Good {timeOfDay.charAt(0).toUpperCase() + timeOfDay.slice(1)}
				</h1>
				<h2 className="text-2xl">Just Wander</h2>
				<ClipSampleGrid clips={clips} />
				<HomeSearchBar />
			</main>
		</div>
	);
}
