import { motion, AnimatePresence } from 'motion/react';
import { X, Mail, Apple } from 'lucide-react';
import { useNavigate } from 'react-router';

interface SignUpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SignUpModal({ isOpen, onClose }: SignUpModalProps) {
  const navigate = useNavigate();

  const handleAction = (action: 'sign-in' | 'sign-up') => {
    onClose();
    navigate(`/${action}`);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl p-6 z-50 max-w-[360px] mx-auto"
          >
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-2"
              style={{ color: '#6B7280' }}
            >
              <X className="w-6 h-6" />
            </button>

            <div className="mb-8">
              <h2
                className="text-[24px] leading-[30px] mb-2"
                style={{ color: '#1D3557', fontWeight: 700 }}
              >
                Save tips for your trip
              </h2>
              <p className="text-[15px] leading-[22px]" style={{ color: '#6B7280' }}>
                Create an account to save tips and access them anytime
              </p>
            </div>

            <div className="flex flex-col gap-3">
              <motion.button
                onClick={() => handleAction('sign-up')}
                className="w-full px-6 py-4 rounded-xl text-[15px] font-medium"
                style={{ backgroundColor: '#457B9D', color: '#fff' }}
                whileTap={{ scale: 0.98 }}
              >
                Create an account
              </motion.button>

              <motion.button
                onClick={() => handleAction('sign-in')}
                className="w-full px-6 py-4 rounded-xl text-[15px] font-medium border-2"
                style={{ borderColor: '#457B9D', color: '#457B9D' }}
                whileTap={{ scale: 0.98 }}
              >
                Sign in
              </motion.button>
            </div>

            <p className="text-[12px] text-center mt-6" style={{ color: '#9CA3AF' }}>
              By continuing, you agree to our terms and privacy policy
            </p>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}