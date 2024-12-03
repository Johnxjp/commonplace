"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";

import ImageThumbnail from "@/ui/ImageThumbnail";

type Item = {
	id: string;
	title: string;
	authors: string[];
	updatedAt: Date;
	lastAccessedAt: Date | null;
	clipCount: number;
	thumbnailUrl: string | null;
};

// const dummyItems: Item[] = [
// 	{
// 		id: "f82befef-c1fe-43e6-8d27-39ea77f65a31",
// 		title: "AI 2041: Ten Visions for Our Future",
// 		authors: ["Kai-Fu Lee", "Chen Qiufan"],
// 		updatedAt: new Date("2022-11-14T04:56:00.000Z"),
// 		clipCount: 5,
// 		lastAccessedAt: null,
// 		thumbnailUrl: null,
// 	},
// 	{
// 		id: "f82befef-c1fe-43e6-8d27-39ea77f64a31",
// 		title: "AI 2041",
// 		authors: ["Kai-Fu Lee"],
// 		updatedAt: new Date("2022-11-14T04:56:00.000Z"),
// 		clipCount: 10,
// 		lastAccessedAt: new Date("2022-11-14T04:56:00.000Z"),
// 		thumbnailUrl: null,
// 	},
// ];

// TODO: Cache the library items across the app once fetched unless
// user logs out or changes something
function LibraryItem({ item }: { item: Item }) {
	return (
		<div className="w-full justify-items-left flex flex-row gap-x-2 hover:cursor-pointer hover:bg-slate-100 p-2">
			<Link
				className="h-full w-full absolute"
				href={`/document/${item.id}`}
			></Link>
			<ImageThumbnail
				src={item.thumbnailUrl ? item.thumbnailUrl : "/vibrant.jpg"}
				alt={item.title}
				height={20}
				width={20}
			/>
			<div className="flex min-h-full flex-col w-full">
				<div>
					<h2 className="font-bold line-clamp-1">{item.title}</h2>
					<p className="italic text-sm">{item.authors.join(", ")}</p>
				</div>
				<div className="text-sm flex grow flex-row gap-x-2 place-items-end">
					<p>{item.clipCount} Annotations</p>
					{item.updatedAt !== null ? (
						<>
							<p>&#183;</p>
							<p title="Updated At">item.updatedAt</p>
						</>
					) : null}
				</div>
			</div>
		</div>
	);
}

export default function Library() {
	const [items, setItems] = useState<Item[]>([]);
	const [searchTerm, setSearchTerm] = useState("");

	const filteredItems = useMemo(() => {
		console.log("searchTerm", searchTerm);
		const normalizedSearch = searchTerm.toLowerCase().trim();

		if (!normalizedSearch) return items;

		return items.filter((item) => {
			const titleMatch = item.title.toLowerCase().includes(normalizedSearch);
			const authorMatch = item.authors.some((author) =>
				author.toLowerCase().includes(normalizedSearch)
			);

			return titleMatch || authorMatch;
		});
	}, [items, searchTerm]);

	useEffect(() => {
		console.log("Calling server for library items");
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/library";
		const requestParams = {
			method: "GET",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};
		// setItems(dummyItems);

		fetch(resourceUrl, requestParams)
			.then((res) => res.json())
			.then((data) => {
				const documents: Item[] = data.map((doc) => {
					const authors = doc.authors ? doc.authors.split(";") : [];
					const thumbnailUrl = (doc.thumbnail_path === "" || doc.thumbnail_path === null) ? null : doc.thumbnail_path;
					return {
						id: doc.id,
						title: doc.title,
						authors: authors,
						updatedAt: doc.updated_at ? new Date(doc.updated_at) : null,
						lastAccessedAt: null,
						clipCount: doc.n_clips,
						thumbnailUrl: thumbnailUrl,
					};
				});
				setItems(documents);
			})
			.catch((err) => console.error(err));
	}, []);

	return (
		<div className="min-h-full w-full min-w-0 flex-1">
			<div className="mx-auto flex flex-col w-full h-full mt-0 pl-8 items-left pt-12 pr-14">
				<div className="p-2" id="header">
					<input
						id="keyword-filter"
						type="search"
						placeholder="Search title and authors..."
						value={searchTerm}
						onChange={(e) => setSearchTerm(e.target.value)}
						className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none"
					/>
				</div>
				<div className="flex-1 w-full h-full">
					<ul className="grid grid-cols-1 divide-y-2">
						{filteredItems.map((item) => (
							<li key={item.id}>
								<LibraryItem item={item} />
							</li>
						))}
					</ul>
				</div>
			</div>
		</div>
	);
}
