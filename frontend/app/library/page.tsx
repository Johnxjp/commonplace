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
		<Link className="h-full w-full" href={`/document/${item.id}`}>
			<div className="w-full flex gap-x-2 hover:cursor-pointer hover:bg-slate-100 p-2">
				<ImageThumbnail
					src={item.thumbnailUrl ? item.thumbnailUrl : "/vibrant.jpg"}
					alt={item.title}
					height={80}
					width={80}
				/>
				<div className="flex min-h-full flex-col w-full">
					<div>
						<h2 className="font-bold line-clamp-1">{item.title}</h2>
						<p className="italic text-sm">{item.authors.join(", ")}</p>
					</div>
					<div className="text-sm flex grow flex-row gap-x-2 place-items-end">
						<p>{item.clipCount} Annotations</p>
						{/* {item.updatedAt !== null ? (
						<>
							<p>&#183;</p>
							<p title="Updated At">Last update: {item.updatedAt.toDateString()}</p>
						</>
					) : null} */}
					</div>
				</div>
			</div>
		</Link>
	);
}

export default function Library() {
	const [items, setItems] = useState<Item[]>([]);
	const [searchTerm, setSearchTerm] = useState("");

	const filteredItems = useMemo(() => {
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
					const thumbnailUrl =
						doc.thumbnail_path === "" || doc.thumbnail_path === null
							? null
							: doc.thumbnail_path;
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

	function handleDelete(itemId: string) {
		// Delete conversation
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + `/document/${itemId}`;
		const requestParams = {
			method: "DELETE",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};
		fetch(resourceUrl, requestParams).then((res) => {
			if (res.ok) {
				console.log("Conversation deleted:", itemId);
				// Remove conversation from state
				const updatedItems = items.filter((item) => item.id !== itemId);
				setItems(updatedItems);
			} else console.error("Error deleting conversation:", itemId);
		});
	}

	return (
		<div className="min-h-full w-full min-w-0 flex-1">
			<div className="mx-auto flex flex-col w-full h-full mt-0 pl-8 items-left pt-12 pr-14">
				<p>Total Items: {items.length}</p>
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
								<div className="flex flex-row items-center gap-x-2">
									<div className="flex grow">
										<LibraryItem item={item} />
									</div>
									<div className="px-2">
										<button
											onClick={(e) => {
												e.stopPropagation();
												handleDelete(item.id);
											}}
											className="max-h-10 rounded-lg py-1 px-2 bg-slate-300 text-sm text-white font-bold hover:bg-red-500"
										>
											Delete
										</button>
									</div>
								</div>
							</li>
						))}
					</ul>
				</div>
			</div>
		</div>
	);
}
