"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

import BookDocument from "@/definitions";

type Item = {
	id: string;
	title: string;
	authors: string[];
	documentType: string;
	updatedAt: Date;
	lastAccessedAt: Date | null;
	clipCount: number;
	thumbnailUrl: string | null;
};

const dummyItems: Item[] = [
	{
		id: "f82befef-c1fe-43e6-8d27-39ea77f65a31",
		title: "AI 2041: Ten Visions for Our Future",
		authors: ["Kai-Fu Lee", "Chen Qiufan"],
		documentType: "book",
		updatedAt: new Date("2022-11-14T04:56:00.000Z"),
		clipCount: 5,
		lastAccessedAt: null,
		thumbnailUrl: null,
	},
	{
		id: "f82befef-c1fe-43e6-8d27-39ea77f64a31",
		title: "AI 2041",
		authors: ["Kai-Fu Lee"],
		documentType: "book",
		updatedAt: new Date("2022-11-14T04:56:00.000Z"),
		clipCount: 10,
		lastAccessedAt: new Date("2022-11-14T04:56:00.000Z"),
		thumbnailUrl: null,
	},
];

function LibraryItem({ item }: { item: Item }) {
	return (
		<div className="w-full flex flex-row gap-x-2 hover:cursor-pointer hover:bg-slate-100 p-2">
			<div className="relative min-w-20 max-w-20 min-h-20 max-h-20">
				<Image
					className="rounded-md"
					src={item.thumbnailUrl !== null ? item.thumbnailUrl : "/vibrant.jpg"}
					// width={75}
					// height={75}
					objectFit="cover"
					layout="fill"
					objectPosition="center"
					alt={item.title}
				/>
			</div>
			<div className="flex min-h-full flex-col w-full">
				<div>
					<h2 className="font-bold line-clamp-1">{item.title}</h2>
					<p className="italic text-sm">{item.authors.join(", ")}</p>
				</div>
				{/* <p>{item.documentType}</p> */}
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

	useEffect(() => {
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/library";
		const requestParams = {
			method: "GET",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};
		setItems(dummyItems);

		fetch(resourceUrl, requestParams)
			.then((res) => res.json())
			.then((data) => {
				console.log(data);
				const documents: Item[] = data.map((doc) => {
					return {
						id: doc.id,
						title: doc.title,
						authors: [doc.authors],
						documentType: doc.document_type,
						updatedAt: doc.updated_at ? new Date(doc.updated_at) : null,
						lastAccessedAt: null,
						clipCount: 10,
						thumbnailUrl: doc.thumbnail_path,
					};
				});
				setItems(documents);
				console.log(documents);
			})
			.catch((err) => console.error(err));
	}, []);

	return (
		<div className="min-h-full w-full min-w-0 flex-1">
			<div className="mx-auto flex flex-col w-full h-full mt-0 pl-8 items-left pt-12 pr-14">
				<div id="header"></div>
				<div className="flex-1 w-full h-full">
					<ul className="grid grid-cols-1 divide-y-2">
						{items.map((item) => (
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
