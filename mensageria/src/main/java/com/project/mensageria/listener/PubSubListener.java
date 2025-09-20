package com.project.mensageria.listener;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.cloud.spring.pubsub.core.PubSubTemplate;
import com.google.cloud.spring.pubsub.support.BasicAcknowledgeablePubsubMessage;
import com.project.mensageria.model.BookingMessage;
import com.project.mensageria.service.BookingService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Component
public class PubSubListener {

    private static final Logger LOGGER = LoggerFactory.getLogger(PubSubListener.class);

    @Autowired
    private PubSubTemplate pubSubTemplate;

    @Autowired
    private BookingService bookingService;

    @Autowired
    private ObjectMapper objectMapper;

    // Pega o valor do application.properties
    @Value("${app.pubsub.subscription-id}")
    private String subscriptionId;

    // Este método será executado automaticamente assim que a aplicação estiver 100% pronta.
    @EventListener(ApplicationReadyEvent.class)
    public void subscribe() {
        LOGGER.info("Inscrevendo-se na assinatura Pub/Sub: {}", subscriptionId);
        // O método subscribe recebe o nome da assinatura e uma função para processar a mensagem
        this.pubSubTemplate.subscribe(subscriptionId, this::handleMessage);
    }

    private void handleMessage(BasicAcknowledgeablePubsubMessage message) {
        String messagePayload = message.getPubsubMessage().getData().toStringUtf8();
        LOGGER.info(">>> Mensagem recebida da fila! ID: {} | Conteúdo: {}", message.getPubsubMessage().getMessageId(), messagePayload);

        try {
            // 1. Converte o JSON para o nosso DTO
            BookingMessage bookingMessage = objectMapper.readValue(messagePayload, BookingMessage.class);

            // 2. Chama o Service para fazer todo o trabalho de salvar no banco
            bookingService.processAndSaveBooking(bookingMessage);

            LOGGER.info("<<< Mensagem processada e salva com sucesso! ID: {}", message.getPubsubMessage().getMessageId());
            // 3. Confirma para o Pub/Sub que a mensagem foi processada com sucesso (ack)
            message.ack();


        } catch (Exception e) {
            LOGGER.error("!!! Erro ao processar mensagem ID: {}. A mensagem será reenviada.", message.getPubsubMessage().getMessageId(), e);

            // 4. Avisa ao Pub/Sub que houve um erro e a mensagem deve ser processada novamente mais tarde (nack)
            message.nack();
        }
    }
}