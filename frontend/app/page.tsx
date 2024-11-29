"use client";

import { useState, useEffect } from "react";

import { getTimeOfDay } from "@/utils";
import BookDocument from "@/definitions";
import BookDocumentCard from "@/ui/BookDocumentCard";
import HomeSearchBar from "@/HomeSearchBar";

function BookDocumentSampleGrid({ documents }: { documents: BookDocument[] }) {
	return (
		<ul className="grid w-full md:grid-cols-3 gap-3">
			{documents.map((doc) => (
				<li className="flex-1" key={doc.id}>
					<BookDocumentCard {...doc} />
				</li>
			))}
		</ul>
	);
}

const dummyDocuments: BookDocument[] = [
	{
		id: "0d7da630-511b-44b1-99d5-82f68afd904a",
		title: "Steve Jobs: The Exclusive Biography",
		authors: ["Walter Isaacson"],
		documentType: "book",
		content:
			"The problem was that the iPhone should have been all about the display, but in their current design the case competed with the display instead of getting out of the way. The whole device felt too masculine, task-driven, efficient. “Guys, you’ve killed yourselves over this design for the last nine months, but we’re going to change it,”",
		createdAt: new Date("2016-12-23T04:56:00.000Z"),
		updatedAt: null,
		isClip: true,
		clipStart: 8040,
		clipEnd: null,
		catalogueId: "584a0951-bb73-4fa6-91ab-f5862b44b544",
	},
	{
		id: "8b6779e8-2fea-4af2-aa53-8c42bb02a32b",
		title: "Good Strategy/Bad Strategy: The difference and why it matters",
		authors: ["Richard Rumelt"],
		documentType: "book",
		content:
			"its like in any game when your losing to a tough opponent you let them gdt comortble and wait untjl they make a mstake due to omisskon or misjudgement.",
		createdAt: new Date("2022-11-04T04:56:00.000Z"),
		updatedAt: null,
		isClip: true,
		clipStart: 378,
		clipEnd: null,
		catalogueId: "775df506-54bd-4833-9ff4-58c1c6c26fbe",
	},
	{
		id: "7f64a2b2-7f82-43ee-8e4c-7377da1d7be0",
		title: "Letters from a Stoic: Epistulae Morales Ad Lucilium (Classics)",
		authors: ["Seneca"],
		documentType: "book",
		content:
			"return from body to mind very soon. Exercise it day and night. Only a moderate amount of work is needed for it to thrive and develop. It is a form of exercise to which cold and heat and even old age are no obstacle. Cultivate an asset which the passing of time itself improves.",
		createdAt: new Date("2024-05-25T04:56:00.000Z"),
		updatedAt: null,
		isClip: true,
		clipStart: 941,
		clipEnd: null,
		catalogueId: "387a049c-3af7-44c5-9a46-a4841a2166b3",
	},
	{
		id: "4e4f711a-5cdd-4904-8d07-83ca3921af3c",
		title: "The Everything Store: Jeff Bezos and the Age of Amazon",
		authors: ["Brad Stone"],
		documentType: "book",
		content:
			"The companies that solved the innovator’s dilemma, Christensen wrote, succeeded when they “set up autonomous organizations charged with building new and independent businesses around the disruptive technology.”",
		createdAt: new Date("2021-01-12T04:56:00.000Z"),
		updatedAt: null,
		isClip: true,
		clipStart: 3526,
		clipEnd: null,
		catalogueId: "ec7d1c6b-273b-4cd3-a01b-044d9ac33769",
	},
	{
		id: "4f8c3392-693f-47f0-873c-68c4a8a0e9fa",
		title: "The Art of Learning: A Journey in the Pursuit of Excellence",
		authors: ["Josh Waitzkin"],
		documentType: "book",
		content:
			"Everyone races to learn more and more, but nothing is done deeply. Things look pretty but they are superficial, without a sound body mechanic or principled foundation.",
		createdAt: new Date("2019-04-20T04:56:00.000Z"),
		updatedAt: null,
		isClip: true,
		clipStart: 1417,
		clipEnd: null,
		catalogueId: "e62a7d2a-06ab-41f2-9084-b8b66efa808a",
	},
	{
		id: "f82befef-c1fe-43e6-8d27-39ea77f65a31",
		title: "AI 2041: Ten Visions for Our Future",
		authors: ["Kai-Fu Lee;Chen Qiufan"],
		documentType: "book",
		content:
			"“What right do you have to share my data link with some insurance company!”",
		createdAt: new Date("2022-11-14T04:56:00.000Z"),
		updatedAt: null,
		isClip: true,
		clipStart: 689,
		clipEnd: null,
		catalogueId: "cedee626-8553-46cd-8ba5-0de88bcebc01",
	},
];

export default function Home() {
	const timeOfDay: string = getTimeOfDay();
	const [documents, setDocuments] = useState<BookDocument[]>(dummyDocuments);

	useEffect(() => {
		const serverUrl = "http://localhost:8000";
		const resourceUrl = serverUrl + "/documents?limit=6&random=true";
		const requestParams = {
			method: "GET",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
		};

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
				<h2 className="text-2xl">Let Your Mind Wander</h2>
				<div className="mx-auto max-w-3xl w-full px-1 md:px-2 flex">
					<BookDocumentSampleGrid documents={documents} />
				</div>
				<HomeSearchBar />
			</main>
		</div>
	);
}
