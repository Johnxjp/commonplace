"""
API routes for enabling conversation over documents using language models
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
import nltk
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.config import THRESHOLD_SCORE
from app.db import get_db, operations
from app.index.llm import (
    answer_question,
    extract_ids_from_llm_response,
    generate_query_variants,
)
from app.index.retrieval import retrieve_candidate_chunks
from app.schemas import MessageRoles

ConversationRouter = APIRouter()
logger = logging.getLogger(__name__)


@ConversationRouter.post("/conversation", status_code=201)
def create_conversation(
    user_id: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Starts a conversation and returns an id to the frontend. Note,
    Anthropic actually pass a UUID from the frontend, but I'll create it
    in the backend. The frontend will have to wait to retrieve it to redirect
    the user to the right page. This will need to log the conversation in
    a database together with the id and state.

    Returns 201 to signal a conversation has begun.

    Payload
    {
    }

    Returns following object
        {
        "uuid": "6ee38188-9447-4abe-84b3-bde551baaf23",
        "name": ""  // Name of the conversation usually assigned by LLM
        "created_at": "2024-12-04T09:11:52.639508Z",
        "updated_at": "2024-12-04T09:11:52.639508Z",
        # "current_leaf_message_uuid": null
    }
    """
    try:
        conversation = operations.create_conversation(db, user_id)
        return {
            "id": conversation.id,
            "name": conversation.name,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "current_leaf_message_id": conversation.current_leaf_message_uuid,  # noqa
            "model": conversation.model,
        }
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=500, detail="Error creating conversation"
        )


class MessagePayload(BaseModel):
    content: str
    sender: str
    parent_message_id: Optional[str] = None


@ConversationRouter.post("/conversation/{conversation_id}/message")
def add_message_to_conversation(
    conversation_id: str,
    message_payload: MessagePayload,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Adds a message to the conversation.
    """
    try:
        content = message_payload.content
        sender = message_payload.sender
        parent_message_id = message_payload.parent_message_id
        message = operations.add_message(
            db,
            user_id,
            conversation_id,
            sender=sender,
            content=content,
            parent_message_id=parent_message_id,
        )
        return {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "parent_id": message.parent_id,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "sender": message.sender,
            "content": message.content,
        }
    except Exception as e:
        logger.error(f"Error adding message to conversation: {e}")
        raise HTTPException(
            status_code=500, detail="Error adding message to conversation"
        )


@ConversationRouter.get("/conversation/{conversation_id}")
def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the conversation with all messages
    """
    conversation = operations.get_conversation(db, user_id, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with id {conversation_id} not found",
        )
    messages = sorted(conversation.messages, key=lambda x: x.created_at)
    return_messages = []
    for message in messages:
        # TODO: This is a major hack. Feels iffy. Should be stored
        if message.sender == MessageRoles.USER.value:
            sources = []
        else:
            sources = []
            source_ids = extract_ids_from_llm_response(message.content)
            logger.info(f"Extracted source ids: {source_ids}")
            for source_id in source_ids:
                clip = operations.get_user_clip_by_id(db, user_id, source_id)
                if not clip:
                    # What to do here. There are a number of reasons this could
                    # be wrong. Either the LLM misquoted the source id or the
                    # source id is not in the database anymore.
                    logger.error(f"Clip with id {source_id} not found")
                else:
                    # TODO: Sources are returned but not in fetch_conversation
                    formatted_source = {
                        "id": clip.id,
                        "content": clip.content,
                        "document_id": clip.document_id,
                        "location_type": clip.location_type,
                        "clip_start": clip.clip_start,
                        "clip_end": clip.clip_end,
                        "created_at": clip.created_at,
                        "updated_at": clip.updated_at,
                        "title": clip.document.title,
                        "authors": clip.document.authors,
                        "catalogue_id": clip.document.catalogue_id,
                        "user_thumbnail_path": clip.document.user_thumbnail_path,
                    }
                    sources.append(formatted_source)
        return_messages.append(
            {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "parent_id": message.parent_id,
                "created_at": message.created_at,
                "sender": message.sender,
                "content": message.content,
                "sources": sources,
            }
        )

    return {
        "id": conversation.id,
        "name": conversation.name,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "current_leaf_message_id": conversation.current_leaf_message_uuid,  # noqa
        "model": conversation.model,
        "summary": conversation.summary,
        "message_count": conversation.message_count,
        "messages": return_messages,
    }


@ConversationRouter.delete("/conversation/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletes a conversation
    """
    try:
        logger.info(f"Deleting conversation with id {conversation_id}")
        operations.delete_conversation(db, user_id, conversation_id)
        return {"message": f"Conversation with id {conversation_id} deleted"}
    except ValueError as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Conversation not found with id {conversation_id}",
        )
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=500, detail="Error deleting conversation"
        )


@ConversationRouter.get("/conversation")
def get_conversations(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort: Optional[str] = None,
    order_by: Optional[str] = None,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns a list of all conversations.

    Does not return entirety of the messages in the conversation just the
    metadata.
    """
    conversations = operations.get_conversations(
        db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        sort=sort,
        order_by=order_by,
    )
    return [
        {
            "id": conversation.id,
            "name": conversation.name,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "current_leaf_message_id": conversation.current_leaf_message_uuid,  # noqa
            "model": conversation.model,
            "summary": conversation.summary,
            "message_count": conversation.message_count,
        }
        for conversation in conversations
    ]


class ConversationUpdatePayload(BaseModel):
    query: str
    parent_message_id: Optional[str] = None


@ConversationRouter.post("/conversation/{conversation_id}/completion")
def complete_conversation(
    conversation_id: str,
    completion_payload: ConversationUpdatePayload,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    This starts the job to answer the question for the LLM and

    This sends the response from the LLM to the frontend together with
    metadata about the state of the conversation e.g. if it's finished
    or note.

    Anthropic also has a parent_message_uuid. This suggests to me that
    they store every message independently and then link them together. The
    parent message is the message immediately before the current message,
    which can be either a user message or the system response.


    (conversation id is in the query parameter)
    Payload:
    {
        prompt: "some user prompt",

        // if allow multiple messages
        parent_uuid: "58ae8848-5fc8-41b5-bbed-3305068a435f",
    }


    Returns chat details and response details
    {
        "uuid": "6ee38188-9447-4abe-84b3-bde551baaf23" // conversation id
        "message_id": "62b661c4-c186-476a-8744-b414d0fa2764",
        "prompt": "some user prompt"
        "response": "llm response" # might be slow without streaming but who
        cares for now
        "sources": [] // sources from the user's knowledge base
    }

    In the response we will have to include sources from the user's
    knowledge base so the frontend can render them


    {
    "type":"message_start",
    "message":{"id":
    "chatcompl_01TF74HAb3VLariRzeashL8N","type":"message",
    "role":"assistant",
    "model":"",
    "parent_uuid":"58ae8848-5fc8-41b5-bbed-3305068a435f",
    "uuid":"62b661c4-c186-476a-8744-b414d0fa2764",
    "content":[],"stop_reason":null,"stop_sequence":null
    }

    System design. Do we allow multiple types of messages e.g. summarise,
    answer, etc? If so, it would change the design. The query passing step
    would need to identify the intent and route the system to the correct
    function.

    Steps required:
    - Parse the query and decompose it. This may require an LLM
    - For each query or subquery, embed the text and perform retrieval
    - Extract content from retrieval and structure
    - Pass this structured text to an LLM to format with the original prompt
    - Write info to the database
    - Return the response to the user

    At the moment this will not be streamed.
    """
    try:
        query = completion_payload.query
        parent_message_id = completion_payload.parent_message_id

        conversation = operations.get_conversation(
            db, user_id, conversation_id
        )
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with id {conversation_id} not found",
            )

        if conversation.name is None:
            name = nltk.sent_tokenize(query)[0]
            conversation = operations.add_conversation_name(
                db, user_id, conversation_id, name
            )

        generated_queries = generate_query_variants(query, max_variants=3)
        # Add query variants and original query
        generated_queries = generated_queries + [query]
        logger.info(f"Generated queries: {generated_queries}")

        # We could make this batch
        candidates = []

        # Need to remove duplicate text
        referenced_chunks = set()
        for q in generated_queries:
            candidates_and_scores = retrieve_candidate_chunks(
                db, user_id, query, topk=5, threshold=THRESHOLD_SCORE
            )
            for result in candidates_and_scores:
                if result.chunk_content in referenced_chunks:
                    continue
                referenced_chunks.add(result.chunk_content)
                candidates.append(result)

            # Log candidates
            for result in candidates_and_scores:
                logger.info(
                    f"Found candidate: ({result.chunk_content}, {result.score})"
                    f" from ({result.source_id}) for query: {q}"
                )

        # Extract context as list of Tuples with (source_id, chunk_text)
        llm_context = [
            {"id": str(result.source_id), "text": result.chunk_content}
            for result in candidates
        ]
        response = answer_question(query, llm_context)
        logger.info(f"Response to question: {response}")

        # Extract ids from the response and retrieve source details
        source_ids = extract_ids_from_llm_response(response)
        logger.info(f"Extracted source ids: {source_ids}")
        invalid_ids = []
        sources = []
        for source_id in source_ids:
            clip = operations.get_user_clip_by_id(db, user_id, source_id)
            if not clip:
                # What to do here. There are a number of reasons this could
                # be wrong. Either the LLM misquoted the source id or the
                # source id is not in the database. We could add a flag to
                # the source id to indicate that it's not in the database.
                logger.error(f"Clip with id {source_id} not found")
                invalid_ids.append(source_id)
            else:
                # TODO: Sources are returned but not in fetch_conversation
                formatted_source = {
                    "id": clip.id,
                    "content": clip.content,
                    "document_id": clip.document_id,
                    "location_type": clip.location_type,
                    "clip_start": clip.clip_start,
                    "clip_end": clip.clip_end,
                    "created_at": clip.created_at,
                    "updated_at": clip.updated_at,
                    "title": clip.document.title,
                    "authors": clip.document.authors,
                    "catalogue_id": clip.document.catalogue_id,
                    "user_thumbnail_path": clip.document.user_thumbnail_path,
                }
                sources.append(formatted_source)

        # Remove invalid ids from response — do we want this?
        for invalid_id in invalid_ids:
            # Unfortunately, this is a bit of a hack. We need to remove the
            # invalid id from the response. We can't just remove the id as
            # it could be in the middle of the response. We need to remove
            # the entire block of text that contains the id plus the
            response = response.replace(f"```{invalid_id}```", "")

        # Add new leaf message to the conversation database
        message = operations.add_message(
            db,
            user_id,
            conversation_id,
            sender=MessageRoles.SYSTEM.value,
            content=response,
            parent_message_id=parent_message_id,
        )

        return {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "parent_id": message.parent_id,
            "created_at": message.created_at,
            "sender": message.sender,
            "prompt": query,
            "content": response,
            "sources": sources,
        }

    except Exception as e:
        logger.error(f"Error completing conversation: {e}")
        raise HTTPException(
            status_code=500, detail="Error completing conversation"
        )


@ConversationRouter.get("/message/{message_id}")
def get_message(
    message_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves a user message
    """
    message = operations.get_message(db, user_id, message_id)
    if not message:
        raise HTTPException(
            status_code=404, detail=f"Message with id {message_id} not found"
        )
    return message


@ConversationRouter.post("/conversation/{conversation_id}/summarisation")
def summarise_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
    Session=Depends(get_db),
):
    """
    This summarises the conversation and returns a summary.

    If the conversation is too long, the summary will be based on a truncated
    version of the conversation which will include the original message and
    response plus the tail of the message. It will prioritise the original
    message and response if too long.
    """
    pass
