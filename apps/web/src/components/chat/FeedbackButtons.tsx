import { Button, Text } from '@fluentui/react-components';
import { ThumbLike16Regular, ThumbDislike16Regular } from '@fluentui/react-icons';
import { useState } from 'react';
import { submitFeedback } from '../../api/feedbackApi';

interface FeedbackButtonsProps {
  token: string;
  messageId: string;
}

export function FeedbackButtons({ token, messageId }: FeedbackButtonsProps) {
  const [submitted, setSubmitted] = useState<'helpful' | 'not_helpful' | null>(null);

  const handleRating = async (rating: 'helpful' | 'not_helpful') => {
    if (submitted) return;
    try {
      await submitFeedback(token, { messageId, rating });
      setSubmitted(rating);
    } catch {
      // silent for MVP
    }
  };

  if (submitted) {
    return (
      <Text size={200} style={{ color: 'var(--eng-text-muted)', marginTop: '0.5rem' }}>
        Thanks for your feedback.
      </Text>
    );
  }

  return (
    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
      <Button
        appearance="subtle"
        size="small"
        icon={<ThumbLike16Regular />}
        onClick={() => handleRating('helpful')}
      >
        Helpful
      </Button>
      <Button
        appearance="subtle"
        size="small"
        icon={<ThumbDislike16Regular />}
        onClick={() => handleRating('not_helpful')}
      >
        Not helpful
      </Button>
    </div>
  );
}
